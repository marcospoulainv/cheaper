from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
import uvicorn
from scraper.jumbo_api import buscar_jumbo
from scraper.unimarc_api import buscar_unimarc
from scraper.lider_api import buscar_lider
from matcher.ean_matcher import emparejar_por_ean

# DB Imports
from db.database import engine, Base, get_db
from db.models import Producto, PrecioHistorico

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Comparador Retail Chile MVP")

# Add CORS middleware to allow requests from the frontend if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servimos los archivos estáticos desde el directorio 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the main frontend MVP application."""
    return FileResponse("static/index.html")

@app.get("/producto")
async def serve_producto():
    """Serves the detailed individual product page."""
    return FileResponse("static/producto.html")

def guardar_historial_precios(db: Session, productos: list):
    """Guarda silenciosamente los productos en la BD para generar historial"""
    hoy = date.today()
    for p in productos:
        ean = p.get("ean")
        precio = p.get("precio")
        retailer = p.get("retailer")
        
        # Omitimos sin ean o precios en 0
        if not ean or not precio:
            continue
            
        # 1. Crear producto si no existe
        db_prod = db.query(Producto).filter(Producto.ean == ean).first()
        if not db_prod:
            db_prod = Producto(
                ean=ean,
                nombre=p.get("nombre", ""),
                imagen=p.get("imagen", "")
            )
            db.add(db_prod)
            
        # 2. Registrar el precio si no se ha registrado hoy
        db_hist = db.query(PrecioHistorico).filter(
            PrecioHistorico.ean == ean,
            PrecioHistorico.retailer == retailer,
            PrecioHistorico.fecha == hoy
        ).first()
        
        if not db_hist:
            nuevo_hist = PrecioHistorico(
                ean=ean,
                retailer=retailer,
                precio=precio,
                url=p.get("url", ""),
                fecha=hoy
            )
            db.add(nuevo_hist)
            
    db.commit()

@app.get("/api/comparar")
def comparar_precios(q: str, db: Session = Depends(get_db)):
    print(f"Buscando: {q}...")
    
    # 1. Traemos los datos de los tres supermercados
    jumbo_data = buscar_jumbo(q)
    unimarc_data = buscar_unimarc(q)
    lider_data = buscar_lider(q)
    
    todos_los_productos = jumbo_data + unimarc_data + lider_data
    
    # [NUEVO] Guardamos el array directo en nuestra BD histórica 
    try:
        guardar_historial_precios(db, todos_los_productos)
    except Exception as e:
        print(f"Error guardando histórica: {e}")
    
    # 2. MATCHING (Emparejamiento por EAN)
    resultado = emparejar_por_ean(todos_los_productos)

    # 3. Formatear la respuesta para el frontend
    return {
        "query": q,
        "productos_emparejados": resultado["productos_emparejados"],
        "productos_sueltos": resultado["productos_sueltos"]
    }

@app.get("/api/historial/{ean}")
def obtener_historial_precio(ean: str, db: Session = Depends(get_db)):
    """Devuelve el historial de precios para un producto agrupado por retailer"""
    producto = db.query(Producto).filter(Producto.ean == ean).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el historial")
        
    historial = db.query(PrecioHistorico).filter(PrecioHistorico.ean == ean).order_by(PrecioHistorico.fecha.asc()).all()
    
    # Agrupar por retailer
    data_retailers = {}
    for h in historial:
        r = h.retailer
        if r not in data_retailers:
            data_retailers[r] = []
        data_retailers[r].append({
            "fecha": h.fecha.isoformat(),
            "precio": h.precio,
            "url": h.url
        })
        
    return {
        "ean": ean,
        "nombre": producto.nombre,
        "imagen": producto.imagen,
        "historial": data_retailers
    }

@app.get("/api/health")
async def health_check():
    """Status endpoint to ensure the API is running."""
    return {"status": "ok", "message": "Comparador API is running"}

if __name__ == "__main__":
    # Arrancar con uvicorn python main.py o uvicorn main:app --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

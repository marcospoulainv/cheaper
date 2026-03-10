import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from thefuzz import fuzz

# Import scrapers
from scraper.jumbo_api import buscar_jumbo
from scraper.unimarc_api import buscar_unimarc
from scraper.lider_api import buscar_lider
from matcher.ean_matcher import normalizar_texto, extraer_metrica

# Import DB
# We add the db dir to sys.path so we can import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine, SessionLocal
from db.models import Producto, PrecioHistorico

def run_tracking_bot():
    print("Iniciando Bot Rastreador de Precios...")
    hoy = date.today()
    
    db = SessionLocal()
    
    try:
        # Get all distinct products from DB
        productos = db.query(Producto).all()
        print(f"Buscando {len(productos)} productos en los catálogos...")
        
        for p in productos:
            ean_to_track = p.ean
            nombre = p.nombre
            
            print(f"\n[BOT] Rastreando: {nombre} (EAN: {ean_to_track})")
            
            # Since searching by EAN directly on search APIs usually works, 
            # we query using the EAN or the name
            
            scraped_items = []
            try:
                scraped_items += buscar_jumbo(ean_to_track)
                time.sleep(1) # Rate limiting
                scraped_items += buscar_unimarc(ean_to_track)
                time.sleep(1)
                scraped_items += buscar_lider(ean_to_track)
                time.sleep(1)
            except Exception as e:
                print(f"Error parseando scrapers para {ean_to_track}: {e}")
                
            # Matching robusto
            target_metric = extraer_metrica(nombre)
            target_norm = normalizar_texto(nombre)
            
            found_retailers = []
            
            for item in scraped_items:
                ean_item = item.get("ean")
                retailer = item.get("retailer")
                precio = item.get("precio")
                url = item.get("url", "")
                
                if not precio: continue
                
                # Check Si es el mismo producto
                es_match = False
                if ean_item == ean_to_track:
                    es_match = True
                else:
                    # Fuzzy match fallback
                    item_metric = extraer_metrica(item.get("nombre"))
                    item_norm = normalizar_texto(item.get("nombre"))
                    
                    if item_metric == target_metric and target_metric != "":
                        similitud = fuzz.token_sort_ratio(item_norm, target_norm)
                        if similitud >= 85:
                            es_match = True
                            
                if es_match and retailer not in found_retailers:
                    # Registrar nuevo precio para HOY
                    db_hist = db.query(PrecioHistorico).filter(
                        PrecioHistorico.ean == ean_to_track,
                        PrecioHistorico.retailer == retailer,
                        PrecioHistorico.fecha == hoy
                    ).first()
                    
                    if not db_hist:
                        nuevo_hist = PrecioHistorico(
                            ean=ean_to_track,
                            retailer=retailer,
                            precio=precio,
                            url=url,
                            fecha=hoy
                        )
                        db.add(nuevo_hist)
                        print(f" -> Nuevo precio de {retailer} guardado: ${precio}")
                    else:
                        print(f" -> {retailer} ya tenía registro para hoy.")
                        
                    found_retailers.append(retailer)
                    
            db.commit()
            print(f"Finalizado tracking para: {nombre}")
            
    except Exception as e:
        print(f"Error fatal en el Bot: {e}")
        db.rollback()
    finally:
        db.close()
        print("Bot finalizado por hoy.")

if __name__ == "__main__":
    run_tracking_bot()

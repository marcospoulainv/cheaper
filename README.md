# cheaper

Comparador de precios (work in progress) con utilidades para probar integraciones de retail.

## Mejoras recientes

- Scripts de prueba (`test_api.py`, `test_unimarc.py`, `lider_test.py`) refactorizados para:
  - no ejecutar requests al importarse;
  - manejar errores de red/HTTP de forma explícita;
  - soportar argumentos por línea de comandos;
  - usar timeouts para evitar bloqueos;
  - funcionar sin dependencias externas (solo librería estándar de Python).

## Uso rápido

```bash
python test_api.py --output response_test.json
python test_unimarc.py
python lider_test.py "leche"
```

## Nota

`main.py` y `tracker_bot.py` dependen de módulos (`scraper`, `matcher`, `db`) que no están incluidos en este snapshot del repositorio.

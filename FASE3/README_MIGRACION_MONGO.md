# Migracion Oracle -> MongoDB

Este proyecto ahora incluye una migracion completa del dominio de mundiales desde Oracle hacia MongoDB.

## Que migra

- `SELECCION` -> coleccion `selecciones`
- `JUGADOR_PAIS` + `DETALLE_JUGADOR` -> coleccion `jugadores`
- `PARTIDO` + `GOL` -> coleccion `partidos`
- `MUNDIAL` + grupos + posiciones + goleadores + premios + equipo ideal + partidos -> coleccion `mundiales`
- `TIPO_PREMIO` -> coleccion `tipos_premio`
- `metadata_migracion` -> resumen de la ejecucion

## Variables de entorno

```powershell
$env:ORACLE_USER="proyecto1bases2"
$env:ORACLE_PASSWORD="1234"
$env:ORACLE_DSN="localhost:1521/XEPDB1"

$env:MONGO_URI="mongodb://localhost:27017/"
$env:MONGO_DB="mundiales_db"
$env:MONGO_RESET="true"
```

## Instalar dependencias

```powershell
pip install oracledb pymongo
```

## Script de estructura

Para crear explicitamente las colecciones e indices:

```powershell
python crear_estructura_mongo.py
```

## Script de carga

```powershell
python migrar_oracle_mongo.py
```

## Consultas del proyecto

Tambien se incluye un script para cumplir con las consultas pedidas en el enunciado:

```powershell
python consultas_mongo.py mundial 2022
python consultas_mongo.py mundial 2022 --grupo A
python consultas_mongo.py mundial 2022 --pais Argentina

python consultas_mongo.py pais Argentina
python consultas_mongo.py pais Argentina --anio 2022
python consultas_mongo.py pais Argentina --sin-detalles
```

## Resultado esperado

Se crean estas colecciones:

- `selecciones`
- `jugadores`
- `partidos`
- `mundiales`
- `tipos_premio`
- `metadata_migracion`

Si `MONGO_RESET=true`, el script limpia estas colecciones antes de volver a cargar los datos.

## Entrega recomendada

Archivos principales:

- `crear_estructura_mongo.py`: crea colecciones e indices
- `migrar_oracle_mongo.py`: carga los datos a MongoDB
- `consultas_mongo.py`: metodos de consulta por mundial y por pais
- `mundiales.sql`: dataset fuente estructurado de la fase anterior

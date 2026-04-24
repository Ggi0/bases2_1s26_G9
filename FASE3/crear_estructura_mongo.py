"""
Script de preparacion de estructura en MongoDB.

Objetivo:
- Crear las colecciones principales del proyecto si no existen.
- Crear los indices necesarios para acelerar consultas frecuentes.

Equivalencias conceptuales:
- Coleccion en MongoDB = tabla en Oracle/SQL.
- Documento en MongoDB = fila o registro.
- Indice en MongoDB = estructura de apoyo para hacer busquedas mas rapidas.
"""

import os

from pymongo import ASCENDING, MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "mundiales_db")

COLLECTIONS = [
    "selecciones",
    "jugadores",
    "partidos",
    "mundiales",
    "tipos_premio",
    "metadata_migracion",
]


def create_collection_if_missing(db, name):
    """
    Crea una coleccion solo si aun no existe en la base de datos.

    En MongoDB las colecciones pueden crearse automaticamente al insertar datos,
    pero aqui se crean de forma explicita para dejar evidencia del paso de
    construccion de estructura solicitado en el enunciado.
    """
    existing = db.list_collection_names()
    if name not in existing:
        db.create_collection(name)
        print(f"Coleccion creada: {name}")
    else:
        print(f"Coleccion ya existe: {name}")


def create_indexes(db):
    """
    Crea los indices principales del proyecto.

    Los indices se agregan sobre campos muy consultados, por ejemplo:
    - nombre de pais/seleccion
    - anio del mundial
    - etapa y fecha de partidos

    Esto ayuda a que las consultas del proyecto respondan mas rapido.
    """
    print("Creando indices...")

    # Coleccion: selecciones
    # Se consulta mucho por nombre del pais y por anios de participacion.
    db.selecciones.create_index([("nombre", ASCENDING)], unique=True, name="uq_selecciones_nombre")
    db.selecciones.create_index([("participaciones.anio", ASCENDING)], name="ix_selecciones_participaciones_anio")

    # Coleccion: jugadores
    # Facilita buscar jugadores por seleccion y nombre, o por anio de mundial.
    db.jugadores.create_index(
        [("seleccion.id", ASCENDING), ("nombre", ASCENDING)],
        name="ix_jugadores_seleccion_nombre",
    )
    db.jugadores.create_index([("mundiales.anio", ASCENDING)], name="ix_jugadores_mundiales_anio")

    # Coleccion: partidos
    # El par (anio, num_partido) identifica cada partido de forma unica.
    # Tambien se indexan local/visitante, etapa y fecha para filtros frecuentes.
    db.partidos.create_index(
        [("anio", ASCENDING), ("num_partido", ASCENDING)],
        unique=True,
        name="uq_partidos_anio_numero",
    )
    db.partidos.create_index(
        [("local.id", ASCENDING), ("visitante.id", ASCENDING)],
        name="ix_partidos_local_visitante",
    )
    db.partidos.create_index([("etapa", ASCENDING)], name="ix_partidos_etapa")
    db.partidos.create_index([("fecha", ASCENDING)], name="ix_partidos_fecha")

    # Coleccion: mundiales
    # Se consulta por anio, campeon y organizador.
    db.mundiales.create_index([("anio", ASCENDING)], unique=True, name="uq_mundiales_anio")
    db.mundiales.create_index([("campeon.id", ASCENDING)], name="ix_mundiales_campeon")
    db.mundiales.create_index([("organizador.id", ASCENDING)], name="ix_mundiales_organizador")

    # Coleccion: tipos de premio
    # El nombre del premio no debe repetirse.
    db.tipos_premio.create_index([("nombre", ASCENDING)], unique=True, name="uq_tipos_premio_nombre")

    # Coleccion: metadata_migracion
    # Permite consultar historico de ejecuciones por fecha.
    db.metadata_migracion.create_index([("fecha_ejecucion", ASCENDING)], name="ix_metadata_fecha")

    print("Indices creados correctamente.")


def main():
    """
    Flujo principal del script:
    1. Conectarse a MongoDB.
    2. Seleccionar la base de datos del proyecto.
    3. Crear las colecciones del modelo documental.
    4. Crear los indices para optimizar consultas.
    """
    client = MongoClient(MONGO_URI)
    try:
        db = client[MONGO_DB]
        print(f"Base de datos destino: {MONGO_DB}")

        # Recorre la lista de colecciones del proyecto y las crea si hacen falta.
        for collection_name in COLLECTIONS:
            create_collection_if_missing(db, collection_name)

        # Luego crea los indices definidos para cada coleccion.
        create_indexes(db)
        print("Estructura MongoDB creada correctamente.")
    finally:
        client.close()


if __name__ == "__main__":
    main()

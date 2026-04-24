import os
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

import oracledb
from pymongo import MongoClient


ORACLE_USER = os.getenv("ORACLE_USER", "proyecto1bases2")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "1234")
ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/XEPDB1")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "mundiales_db")
RESET_COLLECTIONS = os.getenv("MONGO_RESET", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "si",
    "s",
}

DOMAIN_TABLES = [
    "SELECCION",
    "MUNDIAL",
    "GRUPO",
    "POSICION_GRUPO",
    "POSICION_FINAL",
    "PARTIDO",
    "GOL",
    "JUGADOR_PAIS",
    "DETALLE_JUGADOR",
    "GOLEADOR",
    "PREMIO",
    "TIPO_PREMIO",
    "EQUIPO_IDEAL",
    "TARJETA",
]

TARGET_COLLECTIONS = [
    "selecciones",
    "jugadores",
    "mundiales",
    "partidos",
    "tipos_premio",
    "metadata_migracion",
]


def normalize_value(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


def normalize_row(row, columns):
    return {column: normalize_value(value) for column, value in zip(columns, row)}


def to_bool(value):
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"si", "s", "yes", "y", "true", "1"}:
        return True
    if text in {"no", "n", "false", "0"}:
        return False
    return None


def sorted_rows(rows, *keys):
    return sorted(rows, key=lambda row: tuple(row.get(key) for key in keys))


def fetch_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [column[0].lower() for column in cursor.description]
    return [normalize_row(row, columns) for row in cursor.fetchall()]


def selection_ref(selecciones_by_id, selection_id):
    if selection_id is None:
        return None
    seleccion = selecciones_by_id.get(selection_id)
    return {
        "id": selection_id,
        "nombre": seleccion["nombre"] if seleccion else None,
    }


def player_ref(jugadores_by_id, selecciones_by_id, player_id):
    if player_id is None:
        return None
    jugador = jugadores_by_id.get(player_id)
    if not jugador:
        return {"id": player_id, "nombre": None}
    return {
        "id": player_id,
        "nombre": jugador.get("nombre"),
        "seleccion": selection_ref(selecciones_by_id, jugador.get("id_seleccion")),
    }


def premio_ref(tipos_premio_by_id, premio_id):
    if premio_id is None:
        return None
    tipo = tipos_premio_by_id.get(premio_id)
    return {
        "id": premio_id,
        "nombre": tipo["nombre"] if tipo else None,
    }


def build_partido_docs(
    partidos,
    goles_by_partido,
    selecciones_by_id,
    jugadores_by_id,
):
    partido_docs = []

    for partido in sorted_rows(partidos, "anio", "num_partido", "id_partido"):
        local = selection_ref(selecciones_by_id, partido["id_local"])
        visitante = selection_ref(selecciones_by_id, partido["id_visitante"])
        goles = []

        for gol in sorted_rows(goles_by_partido[partido["id_partido"]], "minuto", "id_gol"):
            goles.append(
                {
                    "id_gol": gol["id_gol"],
                    "minuto": gol.get("minuto"),
                    "seleccion": selection_ref(selecciones_by_id, gol.get("id_seleccion")),
                    "jugador": player_ref(jugadores_by_id, selecciones_by_id, gol.get("id_jugador")),
                    "es_penal": to_bool(gol.get("es_penal")),
                    "es_autogol": to_bool(gol.get("es_autogol")),
                    "es_autogol_raw": gol.get("es_autogol"),
                }
            )

        ganador = None
        if partido.get("goles_local") is not None and partido.get("goles_visitante") is not None:
            if partido["goles_local"] > partido["goles_visitante"]:
                ganador = local
            elif partido["goles_visitante"] > partido["goles_local"]:
                ganador = visitante
            elif to_bool(partido.get("penales")):
                if (partido.get("penales_local") or 0) > (partido.get("penales_visitante") or 0):
                    ganador = local
                elif (partido.get("penales_visitante") or 0) > (partido.get("penales_local") or 0):
                    ganador = visitante

        partido_docs.append(
            {
                "_id": partido["id_partido"],
                "id_partido": partido["id_partido"],
                "anio": partido["anio"],
                "num_partido": partido.get("num_partido"),
                "fecha": partido.get("fecha"),
                "etapa": partido.get("etapa"),
                "local": local,
                "visitante": visitante,
                "marcador": {
                    "local": partido.get("goles_local"),
                    "visitante": partido.get("goles_visitante"),
                },
                "definicion": {
                    "tiempo_extra": to_bool(partido.get("tiempo_extra")),
                    "penales": to_bool(partido.get("penales")),
                    "penales_local": partido.get("penales_local"),
                    "penales_visitante": partido.get("penales_visitante"),
                },
                "ganador": ganador,
                "goles": goles,
            }
        )

    return partido_docs


def build_mundial_docs(
    mundiales,
    grupos_by_anio,
    posiciones_grupo_by_anio,
    posiciones_final_by_anio,
    goleadores_by_anio,
    premios_by_anio,
    equipo_ideal_by_anio,
    partidos_by_anio,
    selecciones_by_id,
    jugadores_by_id,
    tipos_premio_by_id,
):
    docs = []

    for mundial in sorted_rows(mundiales, "anio"):
        anio = mundial["anio"]
        grupos = []

        for grupo in sorted_rows(grupos_by_anio[anio], "id_grupo"):
            tabla = []
            for posicion in sorted_rows(
                [row for row in posiciones_grupo_by_anio[anio] if row["id_grupo"] == grupo["id_grupo"]],
                "pts",
                "diferencia",
                "gf",
            ):
                tabla.append(
                    {
                        "id_posicion_grupo": posicion["id_posicion_grupo"],
                        "seleccion": selection_ref(selecciones_by_id, posicion["id_seleccion"]),
                        "pts": posicion.get("pts"),
                        "pj": posicion.get("pj"),
                        "pg": posicion.get("pg"),
                        "pe": posicion.get("pe"),
                        "pp": posicion.get("pp"),
                        "gf": posicion.get("gf"),
                        "gc": posicion.get("gc"),
                        "diferencia": posicion.get("diferencia"),
                        "clasificado": to_bool(posicion.get("clasificado")),
                        "clasificado_raw": posicion.get("clasificado"),
                    }
                )

            tabla.sort(
                key=lambda row: (
                    -(row["pts"] or 0),
                    -(row["diferencia"] or 0),
                    -(row["gf"] or 0),
                    row["seleccion"]["nombre"] or "",
                )
            )

            grupos.append(
                {
                    "id_grupo": grupo["id_grupo"],
                    "selecciones_raw": grupo.get("selecciones"),
                    "tabla": tabla,
                }
            )

        posiciones_finales = []
        for posicion in sorted_rows(posiciones_final_by_anio[anio], "posicion", "id_posicion_final"):
            posiciones_finales.append(
                {
                    "id_posicion_final": posicion["id_posicion_final"],
                    "posicion": posicion.get("posicion"),
                    "seleccion": selection_ref(selecciones_by_id, posicion.get("id_seleccion")),
                }
            )

        goleadores = []
        for goleador in sorted(
            goleadores_by_anio[anio],
            key=lambda row: (-(row.get("goles") or 0), -(row.get("promedio") or 0), row["id_goleador"]),
        ):
            goleadores.append(
                {
                    "id_goleador": goleador["id_goleador"],
                    "jugador": player_ref(jugadores_by_id, selecciones_by_id, goleador.get("id_jugador")),
                    "seleccion": selection_ref(selecciones_by_id, goleador.get("id_seleccion")),
                    "goles": goleador.get("goles"),
                    "partidos": goleador.get("partidos"),
                    "promedio": goleador.get("promedio"),
                }
            )

        premios = []
        for premio in sorted_rows(premios_by_anio[anio], "id_premio"):
            premios.append(
                {
                    "id_premio": premio["id_premio"],
                    "tipo": premio_ref(tipos_premio_by_id, premio.get("id_tipo_premio")),
                    "seleccion": selection_ref(selecciones_by_id, premio.get("id_seleccion")),
                    "jugador": player_ref(jugadores_by_id, selecciones_by_id, premio.get("id_jugador")),
                }
            )

        equipo_ideal = []
        for integrante in sorted_rows(equipo_ideal_by_anio[anio], "posicion", "id_equipo_ideal"):
            equipo_ideal.append(
                {
                    "id_equipo_ideal": integrante["id_equipo_ideal"],
                    "posicion": integrante.get("posicion"),
                    "jugador": player_ref(jugadores_by_id, selecciones_by_id, integrante.get("id_jugador")),
                    "seleccion": selection_ref(selecciones_by_id, integrante.get("id_seleccion")),
                }
            )

        partidos = [dict(partido) for partido in partidos_by_anio[anio]]

        docs.append(
            {
                "_id": anio,
                "anio": anio,
                "organizador": selection_ref(selecciones_by_id, mundial.get("id_organizador")),
                "organizador_raw": mundial.get("organizador"),
                "campeon": selection_ref(selecciones_by_id, mundial.get("id_campeon")),
                "campeon_raw": mundial.get("campeon"),
                "estadisticas": {
                    "num_selecciones": mundial.get("num_selecciones"),
                    "num_partidos": mundial.get("num_partidos"),
                    "goles": mundial.get("goles"),
                    "promedio_gol": mundial.get("promedio_gol"),
                },
                "grupos": grupos,
                "posiciones_finales": posiciones_finales,
                "goleadores": goleadores,
                "premios": premios,
                "equipo_ideal": equipo_ideal,
                "partidos": partidos,
            }
        )

    return docs


def build_jugador_docs(
    jugadores,
    detalles_by_jugador,
    premios_by_jugador,
    tarjetas_by_jugador,
    goles_by_jugador,
    selecciones_by_id,
    tipos_premio_by_id,
):
    docs = []

    for jugador in sorted_rows(jugadores, "id_jugador"):
        mundiales = []
        for detalle in sorted_rows(detalles_by_jugador[jugador["id_jugador"]], "anio"):
            anio = detalle["anio"]
            premios = [
                {
                    "id_premio": premio["id_premio"],
                    "tipo": premio_ref(tipos_premio_by_id, premio.get("id_tipo_premio")),
                    "seleccion": selection_ref(selecciones_by_id, premio.get("id_seleccion")),
                }
                for premio in sorted_rows(
                    [row for row in premios_by_jugador[jugador["id_jugador"]] if row["anio"] == anio],
                    "id_premio",
                )
            ]

            tarjeta = next(
                (
                    row
                    for row in tarjetas_by_jugador[jugador["id_jugador"]]
                    if row["anio"] == anio
                ),
                None,
            )

            goles = [
                {
                    "id_gol": gol["id_gol"],
                    "id_partido": gol.get("id_partido"),
                    "minuto": gol.get("minuto"),
                    "es_penal": to_bool(gol.get("es_penal")),
                    "es_autogol": to_bool(gol.get("es_autogol")),
                }
                for gol in sorted_rows(
                    [row for row in goles_by_jugador[jugador["id_jugador"]] if row["anio"] == anio],
                    "id_partido",
                    "minuto",
                    "id_gol",
                )
            ]

            mundiales.append(
                {
                    "anio": anio,
                    "camiseta": detalle.get("camiseta"),
                    "posicion": detalle.get("posicion"),
                    "jugo": detalle.get("jugo"),
                    "jugo_titular": detalle.get("jugo_titular"),
                    "capitan": detalle.get("capitan"),
                    "no_jugo": detalle.get("no_jugo"),
                    "goles": detalle.get("goles"),
                    "prom_goles": detalle.get("prom_goles"),
                    "tarjeta_amarilla": detalle.get("tarjeta_amarilla"),
                    "tarjeta_roja": detalle.get("tarjeta_roja"),
                    "pg": detalle.get("pg"),
                    "pe": detalle.get("pe"),
                    "pp": detalle.get("pp"),
                    "pos_final": detalle.get("pos_final"),
                    "premios": premios,
                    "tarjetas_torneo": {
                        "amarillas": tarjeta.get("amarillas") if tarjeta else 0,
                        "rojas": tarjeta.get("rojas") if tarjeta else 0,
                    },
                    "goles_partido": goles,
                }
            )

        docs.append(
            {
                "_id": jugador["id_jugador"],
                "id_jugador": jugador["id_jugador"],
                "nombre": jugador.get("nombre"),
                "seleccion": selection_ref(selecciones_by_id, jugador.get("id_seleccion")),
                "altura": jugador.get("altura"),
                "fecha_nacimiento": jugador.get("fecha_nacimiento"),
                "nacionalidad": jugador.get("nacionalidad"),
                "mundiales": mundiales,
            }
        )

    return docs


def build_seleccion_docs(
    selecciones,
    jugadores_by_seleccion,
    posiciones_grupo_by_seleccion,
    posiciones_final_by_seleccion,
    partidos_by_seleccion,
    goleadores_by_seleccion,
    premios_by_seleccion,
    tarjetas_by_seleccion,
    mundiales,
    selecciones_by_id,
    jugadores_by_id,
    tipos_premio_by_id,
):
    mundiales_by_anio = {mundial["anio"]: mundial for mundial in mundiales}
    docs = []

    for seleccion in sorted_rows(selecciones, "id_seleccion"):
        selection_id = seleccion["id_seleccion"]
        anios = set()

        for row in posiciones_grupo_by_seleccion[selection_id]:
            anios.add(row["anio"])
        for row in posiciones_final_by_seleccion[selection_id]:
            anios.add(row["anio"])
        for row in partidos_by_seleccion[selection_id]:
            anios.add(row["anio"])
        for row in goleadores_by_seleccion[selection_id]:
            anios.add(row["anio"])
        for row in premios_by_seleccion[selection_id]:
            anios.add(row["anio"])
        for row in tarjetas_by_seleccion[selection_id]:
            anios.add(row["anio"])
        for mundial in mundiales:
            if mundial.get("id_organizador") == selection_id or mundial.get("id_campeon") == selection_id:
                anios.add(mundial["anio"])

        participaciones = []
        for anio in sorted(anios):
            partidos = [row for row in partidos_by_seleccion[selection_id] if row["anio"] == anio]
            posicion_grupo = sorted_rows(
                [row for row in posiciones_grupo_by_seleccion[selection_id] if row["anio"] == anio],
                "id_grupo",
            )
            posicion_final = next(
                (
                    row
                    for row in posiciones_final_by_seleccion[selection_id]
                    if row["anio"] == anio
                ),
                None,
            )
            tarjetas = next(
                (
                    row
                    for row in tarjetas_by_seleccion[selection_id]
                    if row["anio"] == anio
                ),
                None,
            )

            ganados = empatados = perdidos = gf = gc = 0
            for partido in partidos:
                es_local = partido.get("id_local") == selection_id
                gf_partido = partido.get("goles_local") if es_local else partido.get("goles_visitante")
                gc_partido = partido.get("goles_visitante") if es_local else partido.get("goles_local")
                gf += gf_partido or 0
                gc += gc_partido or 0

                if gf_partido is None or gc_partido is None:
                    continue
                if gf_partido > gc_partido:
                    ganados += 1
                elif gf_partido < gc_partido:
                    perdidos += 1
                else:
                    empatados += 1

            premios = [
                {
                    "id_premio": premio["id_premio"],
                    "tipo": premio_ref(tipos_premio_by_id, premio.get("id_tipo_premio")),
                    "jugador": player_ref(jugadores_by_id, selecciones_by_id, premio.get("id_jugador")),
                }
                for premio in sorted_rows(
                    [row for row in premios_by_seleccion[selection_id] if row["anio"] == anio],
                    "id_premio",
                )
            ]

            goleadores = [
                {
                    "id_goleador": goleador["id_goleador"],
                    "jugador": player_ref(jugadores_by_id, selecciones_by_id, goleador.get("id_jugador")),
                    "goles": goleador.get("goles"),
                    "partidos": goleador.get("partidos"),
                    "promedio": goleador.get("promedio"),
                }
                for goleador in sorted(
                    [row for row in goleadores_by_seleccion[selection_id] if row["anio"] == anio],
                    key=lambda row: (-(row.get("goles") or 0), -(row.get("promedio") or 0), row["id_goleador"]),
                )
            ]

            mundial = mundiales_by_anio.get(anio)
            participaciones.append(
                {
                    "anio": anio,
                    "fue_organizador": bool(mundial and mundial.get("id_organizador") == selection_id),
                    "fue_campeon": bool(mundial and mundial.get("id_campeon") == selection_id),
                    "grupo": [
                        {
                            "id_grupo": row.get("id_grupo"),
                            "pts": row.get("pts"),
                            "pj": row.get("pj"),
                            "pg": row.get("pg"),
                            "pe": row.get("pe"),
                            "pp": row.get("pp"),
                            "gf": row.get("gf"),
                            "gc": row.get("gc"),
                            "diferencia": row.get("diferencia"),
                            "clasificado": to_bool(row.get("clasificado")),
                        }
                        for row in posicion_grupo
                    ],
                    "posicion_final": posicion_final.get("posicion") if posicion_final else None,
                    "desempeno": {
                        "partidos": len(partidos),
                        "ganados": ganados,
                        "empatados": empatados,
                        "perdidos": perdidos,
                        "goles_favor": gf,
                        "goles_contra": gc,
                    },
                    "tarjetas": {
                        "amarillas": tarjetas.get("amarillas") if tarjetas else 0,
                        "rojas": tarjetas.get("rojas") if tarjetas else 0,
                    },
                    "goleadores": goleadores,
                    "premios": premios,
                }
            )

        jugadores = [
            {
                "id_jugador": jugador["id_jugador"],
                "nombre": jugador.get("nombre"),
                "altura": jugador.get("altura"),
                "fecha_nacimiento": jugador.get("fecha_nacimiento"),
                "nacionalidad": jugador.get("nacionalidad"),
            }
            for jugador in sorted_rows(jugadores_by_seleccion[selection_id], "nombre", "id_jugador")
        ]

        docs.append(
            {
                "_id": selection_id,
                "id_seleccion": selection_id,
                "nombre": seleccion.get("nombre"),
                "jugadores": jugadores,
                "participaciones": participaciones,
            }
        )

    return docs


def create_indexes(db):
    db.selecciones.create_index("nombre", unique=True)
    db.jugadores.create_index([("seleccion.id", 1), ("nombre", 1)])
    db.partidos.create_index([("anio", 1), ("num_partido", 1)], unique=True)
    db.partidos.create_index([("local.id", 1), ("visitante.id", 1)])
    db.partidos.create_index("etapa")
    db.mundiales.create_index("campeon.id")
    db.mundiales.create_index("organizador.id")
    db.tipos_premio.create_index("nombre", unique=True)


def main():
    print("Conectando a Oracle...")
    oracle_conn = oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN,
    )
    cursor = oracle_conn.cursor()

    print("Conectando a MongoDB...")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]

    if RESET_COLLECTIONS:
        for collection_name in TARGET_COLLECTIONS:
            db[collection_name].delete_many({})

    tables = {}
    for table_name in DOMAIN_TABLES:
        tables[table_name] = fetch_table(cursor, table_name)
        print(f"{table_name}: {len(tables[table_name])} filas leidas")

    selecciones = tables["SELECCION"]
    mundiales = tables["MUNDIAL"]
    grupos = tables["GRUPO"]
    posiciones_grupo = tables["POSICION_GRUPO"]
    posiciones_final = tables["POSICION_FINAL"]
    partidos = tables["PARTIDO"]
    goles = tables["GOL"]
    jugadores = tables["JUGADOR_PAIS"]
    detalles_jugador = tables["DETALLE_JUGADOR"]
    goleadores = tables["GOLEADOR"]
    premios = tables["PREMIO"]
    tipos_premio = tables["TIPO_PREMIO"]
    equipo_ideal = tables["EQUIPO_IDEAL"]
    tarjetas = tables["TARJETA"]

    selecciones_by_id = {row["id_seleccion"]: row for row in selecciones}
    jugadores_by_id = {row["id_jugador"]: row for row in jugadores}
    tipos_premio_by_id = {row["id_tipo_premio"]: row for row in tipos_premio}

    grupos_by_anio = defaultdict(list)
    for row in grupos:
        grupos_by_anio[row["anio"]].append(row)

    posiciones_grupo_by_anio = defaultdict(list)
    posiciones_grupo_by_seleccion = defaultdict(list)
    for row in posiciones_grupo:
        posiciones_grupo_by_anio[row["anio"]].append(row)
        posiciones_grupo_by_seleccion[row["id_seleccion"]].append(row)

    posiciones_final_by_anio = defaultdict(list)
    posiciones_final_by_seleccion = defaultdict(list)
    for row in posiciones_final:
        posiciones_final_by_anio[row["anio"]].append(row)
        posiciones_final_by_seleccion[row["id_seleccion"]].append(row)

    detalles_by_jugador = defaultdict(list)
    for row in detalles_jugador:
        detalles_by_jugador[row["id_jugador"]].append(row)

    goleadores_by_anio = defaultdict(list)
    goleadores_by_seleccion = defaultdict(list)
    for row in goleadores:
        goleadores_by_anio[row["anio"]].append(row)
        goleadores_by_seleccion[row["id_seleccion"]].append(row)

    premios_by_anio = defaultdict(list)
    premios_by_seleccion = defaultdict(list)
    premios_by_jugador = defaultdict(list)
    for row in premios:
        premios_by_anio[row["anio"]].append(row)
        if row.get("id_seleccion") is not None:
            premios_by_seleccion[row["id_seleccion"]].append(row)
        if row.get("id_jugador") is not None:
            premios_by_jugador[row["id_jugador"]].append(row)

    equipo_ideal_by_anio = defaultdict(list)
    for row in equipo_ideal:
        equipo_ideal_by_anio[row["anio"]].append(row)

    tarjetas_by_jugador = defaultdict(list)
    tarjetas_by_seleccion = defaultdict(list)
    for row in tarjetas:
        if row.get("id_jugador") is not None:
            tarjetas_by_jugador[row["id_jugador"]].append(row)
        if row.get("id_seleccion") is not None:
            tarjetas_by_seleccion[row["id_seleccion"]].append(row)

    goles_by_partido = defaultdict(list)
    goles_by_jugador = defaultdict(list)
    partidos_by_id = {row["id_partido"]: row for row in partidos}
    for row in goles:
        goles_by_partido[row["id_partido"]].append(row)
        if row.get("id_jugador") is not None:
            row_with_year = dict(row)
            row_with_year["anio"] = partidos_by_id.get(row["id_partido"], {}).get("anio")
            goles_by_jugador[row["id_jugador"]].append(row_with_year)

    jugadores_by_seleccion = defaultdict(list)
    for row in jugadores:
        jugadores_by_seleccion[row["id_seleccion"]].append(row)

    partidos_by_seleccion = defaultdict(list)
    for row in partidos:
        if row.get("id_local") is not None:
            partidos_by_seleccion[row["id_local"]].append(row)
        if row.get("id_visitante") is not None:
            partidos_by_seleccion[row["id_visitante"]].append(row)

    partido_docs = build_partido_docs(partidos, goles_by_partido, selecciones_by_id, jugadores_by_id)
    partidos_by_anio = defaultdict(list)
    for doc in partido_docs:
        partidos_by_anio[doc["anio"]].append(doc)

    mundial_docs = build_mundial_docs(
        mundiales,
        grupos_by_anio,
        posiciones_grupo_by_anio,
        posiciones_final_by_anio,
        goleadores_by_anio,
        premios_by_anio,
        equipo_ideal_by_anio,
        partidos_by_anio,
        selecciones_by_id,
        jugadores_by_id,
        tipos_premio_by_id,
    )

    jugador_docs = build_jugador_docs(
        jugadores,
        detalles_by_jugador,
        premios_by_jugador,
        tarjetas_by_jugador,
        goles_by_jugador,
        selecciones_by_id,
        tipos_premio_by_id,
    )

    seleccion_docs = build_seleccion_docs(
        selecciones,
        jugadores_by_seleccion,
        posiciones_grupo_by_seleccion,
        posiciones_final_by_seleccion,
        partidos_by_seleccion,
        goleadores_by_seleccion,
        premios_by_seleccion,
        tarjetas_by_seleccion,
        mundiales,
        selecciones_by_id,
        jugadores_by_id,
        tipos_premio_by_id,
    )

    tipos_premio_docs = [
        {
            "_id": row["id_tipo_premio"],
            "id_tipo_premio": row["id_tipo_premio"],
            "nombre": row.get("nombre"),
        }
        for row in sorted_rows(tipos_premio, "id_tipo_premio")
    ]

    if seleccion_docs:
        db.selecciones.insert_many(seleccion_docs)
    if jugador_docs:
        db.jugadores.insert_many(jugador_docs)
    if partido_docs:
        db.partidos.insert_many(partido_docs)
    if mundial_docs:
        db.mundiales.insert_many(mundial_docs)
    if tipos_premio_docs:
        db.tipos_premio.insert_many(tipos_premio_docs)

    db.metadata_migracion.insert_one(
        {
            "fecha_ejecucion": datetime.utcnow(),
            "origen": {
                "oracle_user": ORACLE_USER,
                "oracle_dsn": ORACLE_DSN,
            },
            "destino": {
                "mongo_uri": MONGO_URI,
                "mongo_db": MONGO_DB,
            },
            "conteos": {
                "selecciones": len(seleccion_docs),
                "jugadores": len(jugador_docs),
                "partidos": len(partido_docs),
                "mundiales": len(mundial_docs),
                "tipos_premio": len(tipos_premio_docs),
            },
        }
    )

    create_indexes(db)

    cursor.close()
    oracle_conn.close()
    mongo_client.close()

    print("Migracion completada correctamente.")
    print(f"Base MongoDB destino: {MONGO_DB}")
    print(f"Selecciones migradas: {len(seleccion_docs)}")
    print(f"Jugadores migrados: {len(jugador_docs)}")
    print(f"Partidos migrados: {len(partido_docs)}")
    print(f"Mundiales migrados: {len(mundial_docs)}")
    print(f"Tipos de premio migrados: {len(tipos_premio_docs)}")


if __name__ == "__main__":
    main()

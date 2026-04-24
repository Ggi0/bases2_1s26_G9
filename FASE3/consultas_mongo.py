import argparse
import os
from typing import Iterable, Optional

from pymongo import MongoClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "mundiales_db")


def get_db():
    client = MongoClient(MONGO_URI)
    return client, client[MONGO_DB]


def normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def bool_to_text(value):
    if value is True:
        return "Si"
    if value is False:
        return "No"
    return "N/D"


def format_score(partido):
    marcador = partido.get("marcador", {})
    local = (partido.get("local") or {}).get("nombre", "N/D")
    visitante = (partido.get("visitante") or {}).get("nombre", "N/D")
    base = f"{local} {marcador.get('local', '-')} - {marcador.get('visitante', '-')} {visitante}"

    definicion = partido.get("definicion", {})
    if definicion.get("penales"):
        base += (
            f" (penales {definicion.get('penales_local', '-')}"
            f" - {definicion.get('penales_visitante', '-')})"
        )
    elif definicion.get("tiempo_extra"):
        base += " (tiempo extra)"

    return base


def safe_text(value, default="N/D"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def print_lines(lines: Iterable[str]):
    for line in lines:
        print(line)


def info_mundial(anio, grupo=None, pais=None, fecha=None, etapa=None):
    client, db = get_db()
    try:
        mundial = db.mundiales.find_one({"anio": anio})
        if not mundial:
            print(f"No se encontro informacion para el mundial {anio}.")
            return

        pais_normalizado = normalize_text(pais)
        grupo_normalizado = normalize_text(grupo)
        etapa_normalizada = normalize_text(etapa)
        fecha_normalizada = normalize_text(fecha)

        print(f"MUNDIAL {anio}")
        print("=" * 60)
        print(f"Organizador: {((mundial.get('organizador') or {}).get('nombre')) or mundial.get('organizador_raw', 'N/D')}")
        print(f"Campeon: {((mundial.get('campeon') or {}).get('nombre')) or mundial.get('campeon_raw', 'N/D')}")

        estadisticas = mundial.get("estadisticas", {})
        print(
            "Estadisticas: "
            f"{estadisticas.get('num_selecciones', 0)} selecciones, "
            f"{estadisticas.get('num_partidos', 0)} partidos, "
            f"{estadisticas.get('goles', 0)} goles, "
            f"promedio {estadisticas.get('promedio_gol', 0)}"
        )

        print("\nGRUPOS")
        print("-" * 60)
        grupos_mostrados = 0
        for grupo_doc in mundial.get("grupos", []):
            if grupo_normalizado and normalize_text(grupo_doc.get("id_grupo")) != grupo_normalizado:
                continue

            tabla = []
            for fila in grupo_doc.get("tabla", []):
                nombre_seleccion = normalize_text((fila.get("seleccion") or {}).get("nombre"))
                if pais_normalizado and nombre_seleccion != pais_normalizado:
                    continue
                tabla.append(fila)

            if not tabla:
                continue

            grupos_mostrados += 1
            print(f"Grupo {grupo_doc.get('id_grupo')}")
            for fila in tabla:
                seleccion = (fila.get("seleccion") or {}).get("nombre", "N/D")
                print(
                    f"  {seleccion:<20} "
                    f"PTS:{fila.get('pts', 0)} PJ:{fila.get('pj', 0)} "
                    f"PG:{fila.get('pg', 0)} PE:{fila.get('pe', 0)} PP:{fila.get('pp', 0)} "
                    f"GF:{fila.get('gf', 0)} GC:{fila.get('gc', 0)} DIF:{fila.get('diferencia', 0)} "
                    f"Clasificado:{bool_to_text(fila.get('clasificado'))}"
                )

        if grupos_mostrados == 0:
            print("No hay grupos que coincidan con los filtros.")

        print("\nPOSICIONES FINALES")
        print("-" * 60)
        posiciones = []
        for fila in mundial.get("posiciones_finales", []):
            nombre = normalize_text((fila.get("seleccion") or {}).get("nombre"))
            if pais_normalizado and nombre != pais_normalizado:
                continue
            posiciones.append(fila)

        if posiciones:
            for fila in posiciones:
                print(f"  {fila.get('posicion', 'N/D')}. {(fila.get('seleccion') or {}).get('nombre', 'N/D')}")
        else:
            print("No hay posiciones finales que coincidan con los filtros.")

        print("\nPARTIDOS")
        print("-" * 60)
        partidos_mostrados = 0
        for partido in mundial.get("partidos", []):
            local = normalize_text((partido.get("local") or {}).get("nombre"))
            visitante = normalize_text((partido.get("visitante") or {}).get("nombre"))
            partido_fecha = normalize_text(partido.get("fecha"))
            partido_etapa = normalize_text(partido.get("etapa"))

            if pais_normalizado and pais_normalizado not in {local, visitante}:
                continue
            if fecha_normalizada and partido_fecha != fecha_normalizada:
                continue
            if etapa_normalizada and partido_etapa != etapa_normalizada:
                continue

            partidos_mostrados += 1
            print(
                f"  {safe_text(partido.get('fecha'))} | {safe_text(partido.get('etapa')):<15} | "
                f"{format_score(partido)}"
            )

        if partidos_mostrados == 0:
            print("No hay partidos que coincidan con los filtros.")

        print("\nTOP GOLEADORES")
        print("-" * 60)
        goleadores_mostrados = 0
        for fila in mundial.get("goleadores", []):
            seleccion = normalize_text((fila.get("seleccion") or {}).get("nombre"))
            if pais_normalizado and seleccion != pais_normalizado:
                continue
            goleadores_mostrados += 1
            print(
                f"  {(fila.get('jugador') or {}).get('nombre', 'N/D'):<25} "
                f"({(fila.get('seleccion') or {}).get('nombre', 'N/D')}) - "
                f"{fila.get('goles', 0)} goles en {fila.get('partidos', 0)} partidos"
            )

        if goleadores_mostrados == 0:
            print("No hay goleadores que coincidan con los filtros.")

        print("\nPREMIOS")
        print("-" * 60)
        premios_mostrados = 0
        for fila in mundial.get("premios", []):
            seleccion = normalize_text((fila.get("seleccion") or {}).get("nombre"))
            jugador = normalize_text((fila.get("jugador") or {}).get("nombre"))
            if pais_normalizado and pais_normalizado not in {seleccion, jugador}:
                continue
            premios_mostrados += 1
            print(
                f"  {(fila.get('tipo') or {}).get('nombre', 'N/D')}: "
                f"jugador={(fila.get('jugador') or {}).get('nombre', 'N/D')} | "
                f"seleccion={(fila.get('seleccion') or {}).get('nombre', 'N/D')}"
            )

        if premios_mostrados == 0:
            print("No hay premios que coincidan con los filtros.")
    finally:
        client.close()


def info_pais(nombre_pais, anio=None, mostrar_detalles=True):
    client, db = get_db()
    try:
        seleccion = db.selecciones.find_one({"nombre": {"$regex": f"^{nombre_pais}$", "$options": "i"}})
        if not seleccion:
            print(f"No se encontro informacion para el pais '{nombre_pais}'.")
            return

        nombre_real = seleccion.get("nombre", nombre_pais)
        participaciones = seleccion.get("participaciones", [])
        if anio is not None:
            participaciones = [row for row in participaciones if row.get("anio") == anio]

        print(f"INFORMACION DE {nombre_real.upper()}")
        print("=" * 60)

        print("ANIOS DE PARTICIPACION")
        print("-" * 60)
        if participaciones:
            for row in participaciones:
                posicion = row.get("posicion_final")
                descripcion = f"Posicion final: {posicion}" if posicion is not None else "Sin posicion final registrada"
                if row.get("fue_campeon"):
                    descripcion = "Campeon"
                print(f"  {row.get('anio')}: {descripcion}")
        else:
            print("  No hay participaciones con ese filtro.")

        print("\nSEDE DE MUNDIALES")
        print("-" * 60)
        sedes = [row.get("anio") for row in participaciones if row.get("fue_organizador")]
        if sedes:
            print("  " + ", ".join(str(anio_sede) for anio_sede in sedes))
        else:
            print("  No ha sido sede en el filtro seleccionado.")

        print("\nDESEMPENO POR MUNDIAL")
        print("-" * 60)
        if participaciones:
            for row in participaciones:
                d = row.get("desempeno", {})
                print(
                    f"  {row.get('anio')}: {d.get('partidos', 0)}PJ | "
                    f"{d.get('ganados', 0)}G {d.get('empatados', 0)}E {d.get('perdidos', 0)}P | "
                    f"{d.get('goles_favor', 0)}GF - {d.get('goles_contra', 0)}GC"
                )
        else:
            print("  Sin datos de desempeno.")

        print("\nFASE DE GRUPOS Y PREMIOS")
        print("-" * 60)
        if participaciones:
            for row in participaciones:
                print(f"  {row.get('anio')}")
                if row.get("grupo"):
                    for grupo in row.get("grupo", []):
                        print(
                            f"    Grupo {grupo.get('id_grupo')}: "
                            f"PTS {grupo.get('pts', 0)}, PJ {grupo.get('pj', 0)}, "
                            f"PG {grupo.get('pg', 0)}, PE {grupo.get('pe', 0)}, PP {grupo.get('pp', 0)}, "
                            f"GF {grupo.get('gf', 0)}, GC {grupo.get('gc', 0)}, DIF {grupo.get('diferencia', 0)}, "
                            f"Clasificado {bool_to_text(grupo.get('clasificado'))}"
                        )
                else:
                    print("    Sin informacion de grupo.")

                if row.get("premios"):
                    for premio in row.get("premios", []):
                        print(
                            f"    Premio: {(premio.get('tipo') or {}).get('nombre', 'N/D')} | "
                            f"Jugador: {(premio.get('jugador') or {}).get('nombre', 'N/D')}"
                        )
                else:
                    print("    Sin premios registrados.")
        else:
            print("  Sin datos para mostrar.")

        print("\nPARTIDOS")
        print("-" * 60)
        query = {
            "$or": [
                {"local.nombre": nombre_real},
                {"visitante.nombre": nombre_real},
            ]
        }
        if anio is not None:
            query["anio"] = anio

        partidos = list(db.partidos.find(query).sort([("anio", 1), ("num_partido", 1)]))
        if partidos:
            for partido in partidos:
                print(
                    f"  {partido.get('anio')} | {safe_text(partido.get('fecha'))} | "
                    f"{safe_text(partido.get('etapa')):<15} | {format_score(partido)}"
                )
        else:
            print("  No hay partidos registrados con ese filtro.")

        if not mostrar_detalles:
            return

        print("\nMAXIMOS GOLEADORES")
        print("-" * 60)
        hubo_goleadores = False
        for row in participaciones:
            goleadores = row.get("goleadores", [])[:3]
            if not goleadores:
                continue
            hubo_goleadores = True
            print(f"  {row.get('anio')}")
            for goleador in goleadores:
                print(
                    f"    {(goleador.get('jugador') or {}).get('nombre', 'N/D')}: "
                    f"{goleador.get('goles', 0)} goles en {goleador.get('partidos', 0)} partidos"
                )
        if not hubo_goleadores:
            print("  No hay goleadores registrados para ese filtro.")

        print("\nTARJETAS DISCIPLINARIAS")
        print("-" * 60)
        if participaciones:
            for row in participaciones:
                tarjetas = row.get("tarjetas", {})
                print(
                    f"  {row.get('anio')}: "
                    f"{tarjetas.get('amarillas', 0)} amarillas | {tarjetas.get('rojas', 0)} rojas"
                )
        else:
            print("  No hay tarjetas registradas para ese filtro.")

        print("\nDETALLE DE JUGADORES")
        print("-" * 60)
        jugadores_query = {"seleccion.nombre": nombre_real}
        jugadores = list(db.jugadores.find(jugadores_query).sort("nombre", 1))
        detalle_impreso = False

        for jugador in jugadores:
            mundiales = jugador.get("mundiales", [])
            if anio is not None:
                mundiales = [row for row in mundiales if row.get("anio") == anio]

            for row in mundiales:
                detalle_impreso = True
                print(
                    f"  {row.get('anio')} | {jugador.get('nombre', 'N/D'):<25} | "
                    f"{row.get('posicion', '-'): <12} | Camiseta {row.get('camiseta', '-')} | "
                    f"Partidos {row.get('jugo', 0)} | Goles {row.get('goles', 0)} | "
                    f"TA {row.get('tarjeta_amarilla', 0)} | TR {row.get('tarjeta_roja', 0)}"
                )

        if not detalle_impreso:
            print("  No hay detalle de jugadores para ese filtro.")
    finally:
        client.close()


def build_parser():
    parser = argparse.ArgumentParser(description="Consultas de mundiales en MongoDB")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    mundial_parser = subparsers.add_parser("mundial", help="Consultar informacion por mundial")
    mundial_parser.add_argument("anio", type=int, help="Anio del mundial")
    mundial_parser.add_argument("--grupo", help="Filtrar por grupo")
    mundial_parser.add_argument("--pais", help="Filtrar por pais")
    mundial_parser.add_argument("--fecha", help="Filtrar por fecha")
    mundial_parser.add_argument("--etapa", help="Filtrar por etapa")

    pais_parser = subparsers.add_parser("pais", help="Consultar informacion por pais")
    pais_parser.add_argument("nombre_pais", help="Nombre del pais")
    pais_parser.add_argument("--anio", type=int, help="Filtrar por anio")
    pais_parser.add_argument(
        "--sin-detalles",
        action="store_true",
        help="Oculta goleadores, tarjetas y detalle de jugadores",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.comando == "mundial":
        info_mundial(
            args.anio,
            grupo=args.grupo,
            pais=args.pais,
            fecha=args.fecha,
            etapa=args.etapa,
        )
        return

    if args.comando == "pais":
        info_pais(
            args.nombre_pais,
            anio=args.anio,
            mostrar_detalles=not args.sin_detalles,
        )


if __name__ == "__main__":
    main()

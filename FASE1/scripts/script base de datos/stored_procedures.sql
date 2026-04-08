-- ============================================================
-- STORED PROCEDURE 1: Información del Mundial por Año
-- ============================================================
-- Recibe: 
--   p_anio: Año del mundial (obligatorio)
--   p_id_grupo: Grupo específico (opcional, NULL = todos)
--   p_id_seleccion: País específico (opcional, NULL = todos)
--   p_etapa: Etapa del torneo (opcional, NULL = todas)
-- ============================================================

CREATE OR REPLACE PROCEDURE sp_info_mundial (
    p_anio              IN NUMBER,
    p_id_grupo          IN VARCHAR2 DEFAULT NULL,
    p_id_seleccion      IN NUMBER DEFAULT NULL,
    p_etapa             IN VARCHAR2 DEFAULT NULL
)
AS
    v_count NUMBER;
BEGIN
    -- Verificar que el año existe
    SELECT COUNT(*) INTO v_count FROM MUNDIAL WHERE ANIO = p_anio;
    IF v_count = 0 THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: Año ' || p_anio || ' no encontrado en la base de datos.');
        RETURN;
    END IF;

    -- ========== INFORMACIÓN GENERAL DEL MUNDIAL ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('════════════════════════════════════════════════════════════');
    DBMS_OUTPUT.PUT_LINE('MUNDIAL ' || p_anio);
    DBMS_OUTPUT.PUT_LINE('════════════════════════════════════════════════════════════');
    
    FOR rec IN (
        SELECT 
            m.ANIO,
            s_org.NOMBRE AS ORGANIZADOR,
            s_cam.NOMBRE AS CAMPEON,
            m.NUM_SELECCIONES,
            m.NUM_PARTIDOS,
            m.GOLES,
            m.PROMEDIO_GOL
        FROM MUNDIAL m
        LEFT JOIN SELECCION s_org ON m.ID_ORGANIZADOR = s_org.ID_SELECCION
        LEFT JOIN SELECCION s_cam ON m.ID_CAMPEON = s_cam.ID_SELECCION
        WHERE m.ANIO = p_anio
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('Organizador: ' || rec.ORGANIZADOR);
        DBMS_OUTPUT.PUT_LINE('Campeón: ' || rec.CAMPEON);
        DBMS_OUTPUT.PUT_LINE('Selecciones: ' || rec.NUM_SELECCIONES);
        DBMS_OUTPUT.PUT_LINE('Partidos: ' || rec.NUM_PARTIDOS);
        DBMS_OUTPUT.PUT_LINE('Goles totales: ' || rec.GOLES);
        DBMS_OUTPUT.PUT_LINE('Promedio de goles por partido: ' || rec.PROMEDIO_GOL);
    END LOOP;

    -- ========== GRUPOS ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    DBMS_OUTPUT.PUT_LINE('GRUPOS');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    
    FOR rec_grupo IN (
        SELECT DISTINCT ID_GRUPO, SELECCIONES
        FROM GRUPO
        WHERE ANIO = p_anio
        AND (p_id_grupo IS NULL OR ID_GRUPO = p_id_grupo)
        ORDER BY ID_GRUPO
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('');
        DBMS_OUTPUT.PUT_LINE('GRUPO ' || rec_grupo.ID_GRUPO || ': ' || rec_grupo.SELECCIONES);
        
        -- Tabla de posiciones del grupo
        FOR rec_pos IN (
            SELECT 
                pg.ID_SELECCION,
                s.NOMBRE,
                pg.PJ, pg.PG, pg.PE, pg.PP,
                pg.GF, pg.GC, pg.DIFERENCIA, pg.PTS,
                DECODE(pg.CLASIFICADO, 'Si', 'Clasificado', 'No', 'No Clasificado') AS CLASIFICADO
            FROM POSICION_GRUPO pg
            JOIN SELECCION s ON pg.ID_SELECCION = s.ID_SELECCION
            WHERE pg.ANIO = p_anio
            AND pg.ID_GRUPO = rec_grupo.ID_GRUPO
            ORDER BY pg.PTS DESC, pg.DIFERENCIA DESC
        ) LOOP
            DBMS_OUTPUT.PUT_LINE('  ' || RPAD(rec_pos.NOMBRE, 25) || 
                ' PJ:' || rec_pos.PJ || ' PG:' || rec_pos.PG || 
                ' PE:' || rec_pos.PE || ' PP:' || rec_pos.PP ||
                ' GF:' || rec_pos.GF || ' GC:' || rec_pos.GC ||
                ' DIF:' || rec_pos.DIFERENCIA || ' PTS:' || rec_pos.PTS ||
                ' ' || rec_pos.CLASIFICADO);
        END LOOP;
    END LOOP;

    -- ========== PARTIDOS ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    DBMS_OUTPUT.PUT_LINE('PARTIDOS');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    
    FOR rec_partido IN (
        SELECT 
            p.NUM_PARTIDO,
            p.FECHA,
            p.ETAPA,
            s_local.NOMBRE AS LOCAL,
            s_visit.NOMBRE AS VISITANTE,
            p.GOLES_LOCAL,
            p.GOLES_VISITANTE,
            DECODE(p.PENALES, 'Si', ' ('|| p.PENALES_LOCAL ||'-'|| p.PENALES_VISITANTE ||' p)', '') AS PENALES_STR
        FROM PARTIDO p
        LEFT JOIN SELECCION s_local ON p.ID_LOCAL = s_local.ID_SELECCION
        LEFT JOIN SELECCION s_visit ON p.ID_VISITANTE = s_visit.ID_SELECCION
        WHERE p.ANIO = p_anio
        AND (p_id_grupo IS NULL OR 
             p.ID_LOCAL IN (SELECT ID_SELECCION FROM POSICION_GRUPO 
                           WHERE ANIO = p_anio AND ID_GRUPO = p_id_grupo)
             OR
             p.ID_VISITANTE IN (SELECT ID_SELECCION FROM POSICION_GRUPO 
                               WHERE ANIO = p_anio AND ID_GRUPO = p_id_grupo))
        AND (p_id_seleccion IS NULL OR p.ID_LOCAL = p_id_seleccion OR p.ID_VISITANTE = p_id_seleccion)
        AND (p_etapa IS NULL OR p.ETAPA = p_etapa)
        ORDER BY p.FECHA, p.NUM_PARTIDO
    ) LOOP
        DBMS_OUTPUT.PUT_LINE(
            RPAD(rec_partido.LOCAL, 20) || ' ' ||
            rec_partido.GOLES_LOCAL || '-' || rec_partido.GOLES_VISITANTE || ' ' ||
            RPAD(rec_partido.VISITANTE, 20) ||
            '  [' || rec_partido.FECHA || ' | ' || rec_partido.ETAPA || ']' ||
            rec_partido.PENALES_STR
        );
    END LOOP;

    -- ========== TOP GOLEADORES ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    DBMS_OUTPUT.PUT_LINE('TOP GOLEADORES');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    
    FOR rec_gol IN (
        SELECT 
            g.ID_JUGADOR,
            jp.NOMBRE AS JUGADOR,
            s.NOMBRE AS SELECCION,
            g.GOLES,
            g.PARTIDOS,
            g.PROMEDIO
        FROM GOLEADOR g
        JOIN JUGADOR_PAIS jp ON g.ID_JUGADOR = jp.ID_JUGADOR
        JOIN SELECCION s ON g.ID_SELECCION = s.ID_SELECCION
        WHERE g.ANIO = p_anio
        AND (p_id_seleccion IS NULL OR g.ID_SELECCION = p_id_seleccion)
        ORDER BY g.GOLES DESC, g.PROMEDIO DESC
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('  ' || RPAD(rec_gol.JUGADOR, 25) || 
            ' (' || rec_gol.SELECCION || ') - ' || 
            rec_gol.GOLES || ' goles en ' || rec_gol.PARTIDOS || ' partidos');
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('════════════════════════════════════════════════════════════');

EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
END sp_info_mundial;
/


-- ============================================================
-- STORED PROCEDURE 2: Información de un País
-- ============================================================
-- Recibe:
--   p_id_seleccion: ID de la selección (obligatorio)
--   p_anio: Año específico (opcional, NULL = todos)
--   p_mostrar_detalles: 'S' = mostrar jugadores, 'N' = resumen
-- ============================================================

CREATE OR REPLACE PROCEDURE sp_info_pais (
    p_id_seleccion      IN NUMBER,
    p_anio              IN NUMBER DEFAULT NULL,
    p_mostrar_detalles  IN VARCHAR2 DEFAULT 'S'
)
AS
    v_nombre_pais VARCHAR2(100);
    v_count NUMBER;
BEGIN
    -- Verificar que el país existe
    SELECT NOMBRE INTO v_nombre_pais FROM SELECCION WHERE ID_SELECCION = p_id_seleccion;

    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('════════════════════════════════════════════════════════════');
    DBMS_OUTPUT.PUT_LINE('INFORMACIÓN DE ' || UPPER(v_nombre_pais));
    DBMS_OUTPUT.PUT_LINE('════════════════════════════════════════════════════════════');

    -- ========== MUNDIALES EN QUE PARTICIPÓ ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('AÑOS DE PARTICIPACIÓN:');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    
    FOR rec_anio IN (
        SELECT DISTINCT pg.ANIO, pf.POSICION
        FROM POSICION_GRUPO pg
        LEFT JOIN POSICION_FINAL pf ON pg.ANIO = pf.ANIO AND pg.ID_SELECCION = pf.ID_SELECCION
        WHERE pg.ID_SELECCION = p_id_seleccion
        AND (p_anio IS NULL OR pg.ANIO = p_anio)
        ORDER BY pg.ANIO DESC
    ) LOOP
        DBMS_OUTPUT.PUT_LINE('  ' || rec_anio.ANIO || 
            CASE WHEN rec_anio.POSICION = 1 THEN ' - CAMPEON'
                 WHEN rec_anio.POSICION = 2 THEN ' - SUBCAMPEON'
                 WHEN rec_anio.POSICION <= 4 THEN ' - SEMIFINALISTA'
                 ELSE ' (Posicion: ' || rec_anio.POSICION || ')'
            END);
    END LOOP;

    -- ========== SEDE DE MUNDIALES ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('SEDE DE MUNDIALES:');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    
    SELECT COUNT(*) INTO v_count FROM MUNDIAL WHERE ID_ORGANIZADOR = p_id_seleccion;
    
    IF v_count > 0 THEN
        FOR rec_sede IN (
            SELECT ANIO FROM MUNDIAL WHERE ID_ORGANIZADOR = p_id_seleccion
        ) LOOP
            DBMS_OUTPUT.PUT_LINE('  Organizador en ' || rec_sede.ANIO);
        END LOOP;
    ELSE
        DBMS_OUTPUT.PUT_LINE('  No ha sido sede');
    END IF;

    -- ========== DESEMPEÑO POR MUNDIAL ==========
    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('DESEMPEÑO POR MUNDIAL:');
    DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
    
    FOR rec_desem IN (
        SELECT 
            m.ANIO,
            COUNT(CASE WHEN (p.ID_LOCAL = p_id_seleccion OR p.ID_VISITANTE = p_id_seleccion) THEN 1 END) AS PARTIDOS,
            SUM(CASE WHEN (p.ID_LOCAL = p_id_seleccion AND p.GOLES_LOCAL > p.GOLES_VISITANTE) 
                     OR (p.ID_VISITANTE = p_id_seleccion AND p.GOLES_VISITANTE > p.GOLES_LOCAL) 
                     THEN 1 ELSE 0 END) AS GANADOS,
            SUM(CASE WHEN (p.ID_LOCAL = p_id_seleccion AND p.GOLES_LOCAL = p.GOLES_VISITANTE) 
                     OR (p.ID_VISITANTE = p_id_seleccion AND p.GOLES_VISITANTE = p.GOLES_LOCAL) 
                     THEN 1 ELSE 0 END) AS EMPATADOS,
            SUM(CASE WHEN (p.ID_LOCAL = p_id_seleccion AND p.GOLES_LOCAL < p.GOLES_VISITANTE) 
                     OR (p.ID_VISITANTE = p_id_seleccion AND p.GOLES_VISITANTE < p.GOLES_LOCAL) 
                     THEN 1 ELSE 0 END) AS PERDIDOS,
            SUM(CASE WHEN p.ID_LOCAL = p_id_seleccion THEN p.GOLES_LOCAL 
                     WHEN p.ID_VISITANTE = p_id_seleccion THEN p.GOLES_VISITANTE 
                     ELSE 0 END) AS GOLES,
            SUM(CASE WHEN p.ID_LOCAL = p_id_seleccion THEN p.GOLES_VISITANTE 
                     WHEN p.ID_VISITANTE = p_id_seleccion THEN p.GOLES_LOCAL 
                     ELSE 0 END) AS GOLES_CONTRA
        FROM MUNDIAL m
        LEFT JOIN PARTIDO p ON m.ANIO = p.ANIO
        WHERE (p.ID_LOCAL = p_id_seleccion OR p.ID_VISITANTE = p_id_seleccion OR p.ANIO IS NULL)
        AND (p_anio IS NULL OR m.ANIO = p_anio)
        GROUP BY m.ANIO
        ORDER BY m.ANIO DESC
    ) LOOP
        IF rec_desem.PARTIDOS > 0 THEN
            DBMS_OUTPUT.PUT_LINE('  ' || rec_desem.ANIO || ': ' || 
                rec_desem.PARTIDOS || 'PJ | ' ||
                rec_desem.GANADOS || 'G ' || 
                rec_desem.EMPATADOS || 'E ' || 
                rec_desem.PERDIDOS || 'P | ' ||
                rec_desem.GOLES || 'GF - ' || rec_desem.GOLES_CONTRA || 'GC');
        END IF;
    END LOOP;

    -- ========== MEJORES GOLEADORES DEL PAÍS ==========
    IF p_mostrar_detalles = 'S' THEN
        DBMS_OUTPUT.PUT_LINE('');
        DBMS_OUTPUT.PUT_LINE('MÁXIMOS GOLEADORES:');
        DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
        
        FOR rec_gol IN (
            SELECT 
                ANIO,
                NOMBRE AS JUGADOR,
                GOLES
            FROM (
                SELECT 
                    g.ANIO,
                    jp.NOMBRE,
                    g.GOLES,
                    ROW_NUMBER() OVER (PARTITION BY g.ANIO ORDER BY g.GOLES DESC) AS RN
                FROM GOLEADOR g
                JOIN JUGADOR_PAIS jp ON g.ID_JUGADOR = jp.ID_JUGADOR
                WHERE g.ID_SELECCION = p_id_seleccion
                AND (p_anio IS NULL OR g.ANIO = p_anio)
            )
            WHERE RN <= 3
            ORDER BY ANIO DESC
        ) LOOP
            DBMS_OUTPUT.PUT_LINE('  ' || rec_gol.ANIO || ': ' || 
                RPAD(rec_gol.JUGADOR, 25) || ' - ' || rec_gol.GOLES || ' goles');
        END LOOP;

        -- ========== TARJETAS DISCIPLINARIAS ==========
        DBMS_OUTPUT.PUT_LINE('');
        DBMS_OUTPUT.PUT_LINE('TARJETAS DISCIPLINARIAS:');
        DBMS_OUTPUT.PUT_LINE('────────────────────────────────────────────────────────────');
        
        FOR rec_tarjeta IN (
            SELECT 
                ANIO,
                SUM(AMARILLAS) AS AMARILLAS,
                SUM(ROJAS) AS ROJAS
            FROM TARJETA
            WHERE ID_SELECCION = p_id_seleccion
            AND (p_anio IS NULL OR ANIO = p_anio)
            GROUP BY ANIO
            ORDER BY ANIO DESC
        ) LOOP
            DBMS_OUTPUT.PUT_LINE('  ' || rec_tarjeta.ANIO || ': ' || 
                rec_tarjeta.AMARILLAS || ' Amarillas | ' || rec_tarjeta.ROJAS || ' Rojas');
        END LOOP;
    END IF;

    DBMS_OUTPUT.PUT_LINE('');
    DBMS_OUTPUT.PUT_LINE('════════════════════════════════════════════════════════════');

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: País con ID ' || p_id_seleccion || ' no encontrado.');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
END sp_info_pais;
/


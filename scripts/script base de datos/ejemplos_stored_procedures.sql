-- ============================================================
-- EJEMPLOS DE USO DE LOS STORED PROCEDURES
-- ============================================================

-- ========== PROCEDURE 1: sp_info_mundial ==========

-- Ejemplo 1: Información completa del Mundial 2022
SET PAGESIZE 0
SET LINESIZE 200
SET LONG 20000
EXEC sp_info_mundial(2022);

-- Ejemplo 2: Mundo 2022 solo del Grupo A
EXEC sp_info_mundial(2022, 'A');

-- Ejemplo 3: Mundo 2022 solo de Argentina
EXEC sp_info_mundial(2022, NULL, 6);  -- ID 6 es Argentina

-- Ejemplo 4: Mundo 2022 de Argentina solo eliminatorias
EXEC sp_info_mundial(2022, NULL, 6, 'Fase final');

-- Ejemplo 5: Mundo 1986 (información histórica)
EXEC sp_info_mundial(1986);

-- Ejemplo 6: Mundo 2010 solo de Brasil, Grupo G
EXEC sp_info_mundial(2010, 'G', 11);  -- ID 11 es Brasil


-- ========== PROCEDURE 2: sp_info_pais ==========

-- Ejemplo 1: Información completa de Argentina
SET PAGESIZE 0
SET LINESIZE 200
SET LONG 20000
EXEC sp_info_pais(6);  -- ID 6 = Argentina

-- Ejemplo 2: Información de Brasil solo en 2002
EXEC sp_info_pais(11, 2002);  -- ID 11 = Brasil

-- Ejemplo 3: Información de Alemania sin detalles
EXEC sp_info_pais(1, NULL, 'N');  -- ID 1 = Alemania, sin detalles

-- Ejemplo 4: Información de Uruguay en 1950
EXEC sp_info_pais(80, 1950);  -- ID 80 = Uruguay

-- Ejemplo 5: Información histórica de Inglaterra
EXEC sp_info_pais(44);  -- ID 44 = Inglaterra

-- Ejemplo 6: Información de España en 2010 con detalles
EXEC sp_info_pais(34, 2010, 'S');  -- ID 34 = España


-- ========== PARA ENCONTRAR IDS DE PAÍSES ==========
SELECT ID_SELECCION, NOMBRE FROM SELECCION WHERE NOMBRE LIKE 'Argen%';
SELECT ID_SELECCION, NOMBRE FROM SELECCION WHERE NOMBRE = 'Brasil';
SELECT ID_SELECCION, NOMBRE FROM SELECCION ORDER BY NOMBRE;


-- ========== PARÁMETROS DISPONIBLES ==========

/*
sp_info_mundial  (
    p_anio          NUMBER,           -- OBLIGATORIO: Año (ej: 2022)
    p_id_grupo      VARCHAR2 DEFAULT, -- OPCIONAL: Grupo (ej: 'A', 'B', NULL=todos)
    p_id_seleccion  NUMBER DEFAULT,   -- OPCIONAL: ID País (ej: 6=Argentina)
    p_etapa         VARCHAR2 DEFAULT  -- OPCIONAL: Etapa (ej: 'Grupo', 'Fase final')
)

sp_info_pais (
    p_id_seleccion      NUMBER,       -- OBLIGATORIO: ID del país
    p_anio              NUMBER,       -- OPCIONAL: Año específico (NULL=todos)
    p_mostrar_detalles  VARCHAR2      -- OPCIONAL: 'S'=con detalles, 'N'=resumen
)
*/

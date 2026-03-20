# Documentación de Stored Procedures

## 1. SP_INFO_MUNDIAL - Información del Mundial por Año

### Descripción
Despliega toda la información relacionada con un mundial específico: información general, grupos, posiciones, partidos, resultados y goleadores.

### Parámetros

| Parámetro | Tipo | Obligatorio | Descripción | Ejemplo |
|-----------|------|-------------|-------------|---------|
| `p_anio` | NUMBER | Si | Año del mundial | 2022 |
| `p_id_grupo` | VARCHAR2 | Opcional | Filtrar por grupo (A, B, C, etc.) | 'A' |
| `p_id_seleccion` | NUMBER | Opcional | Filtrar por ID de país | 6 (Argentina) |
| `p_etapa` | VARCHAR2 | Opcional | Filtrar por etapa | 'Grupo', 'Fase final' |

### Ejemplos de Uso

```sql
-- Mostrar todo sobre el Mundial 2022
EXEC sp_info_mundial(2022);

-- Mostrar mundial 2022 solo del Grupo A
EXEC sp_info_mundial(2022, 'A');

-- Mostrar mondiale 2022 de Argentina (ID 6)
EXEC sp_info_mundial(2022, NULL, 6);

-- Mostrar mundial 2022 de Argentina en Fase final
EXEC sp_info_mundial(2022, NULL, 6, 'Fase final');
```

### Output
Genera un reporte con:
- Información general del mundial (organizador, campeón, total de equipos)
- Grupos y tabla de posiciones
- Partidos con resultados
- Top goleadores

---

## 2. SP_INFO_PAIS - Información de un País

### Descripción
Despliega toda la información de un país a través de los mundiales: años de participación, posiciones, si fue sede, desempeño por año, goleadores y tarjetas.

### Parámetros

| Parámetro | Tipo | Obligatorio | Descripción | Ejemplo |
|-----------|------|-------------|-------------|---------|
| `p_id_seleccion` | NUMBER | Si | ID del país | 6 (Argentina) |
| `p_anio` | NUMBER | Opcional | Filtrar por año específico | 2022 |
| `p_mostrar_detalles` | VARCHAR2 | Opcional | 'S' = detalles, 'N' = resumen | 'S' |

### Ejemplos de Uso

```sql
-- Mostrar toda la información de Argentina
EXEC sp_info_pais(6);

-- Mostrar información de Brasil solo en 2002
EXEC sp_info_pais(11, 2002);

-- Mostrar información de Alemania sin detalles de goleadores/tarjetas
EXEC sp_info_pais(1, NULL, 'N');

-- Mostrar información de Uruguay en 1950
EXEC sp_info_pais(80, 1950);
```

### Output
Genera un reporte con:
- Años de participación (con posiciones finales)
- Mundiales organizados (si aplica)
- Desempeño por mundial (partidos, victorias, goles)
- Máximos goleadores (si p_mostrar_detalles = 'S')
- Tarjetas disciplinarias (si p_mostrar_detalles = 'S')

---

## 3. Encontrar IDs de Países

Para saber qué ID usar en los parámetros:

```sql
-- Ver todos los países
SELECT ID_SELECCION, NOMBRE FROM SELECCION ORDER BY NOMBRE;

-- Buscar un país específico
SELECT ID_SELECCION, NOMBRE FROM SELECCION WHERE NOMBRE LIKE '%Argen%';
SELECT ID_SELECCION, NOMBRE FROM SELECCION WHERE NOMBRE = 'Brasil';
```

### IDs más comunes:
- 1 = Alemania
- 6 = Argentina
- 11 = Brasil
- 34 = España
- 36 = Francia
- 44 = Inglaterra
- 51 = Italia
- 69 = Rusia
- 74 = Suiza
- 80 = Uruguay
- 85 = Yugoslavia

---

## 4. Cómo Crear los Procedures

### En SQL Developer o SQL*Plus:

```sql
-- 1. Copiar el contenido del archivo stored_procedures.sql
-- 2. Ejecutar en tu conexión a la BD

@C:/ruta/al/archivo/stored_procedures.sql

-- 3. Verificar que se crearon correctamente
SELECT OBJECT_NAME FROM USER_OBJECTS 
WHERE OBJECT_TYPE = 'PROCEDURE' 
AND OBJECT_NAME LIKE 'SP_INFO%';
```

### O crear manualmente:

```sql
-- Para el primer procedure
CREATE OR REPLACE PROCEDURE sp_info_mundial (
    p_anio              IN NUMBER,
    p_id_grupo          IN VARCHAR2 DEFAULT NULL,
    p_id_seleccion      IN NUMBER DEFAULT NULL,
    p_etapa             IN VARCHAR2 DEFAULT NULL
)
AS
BEGIN
    -- ... código del procedure ...
END sp_info_mundial;
/

-- Para el segundo procedure
CREATE OR REPLACE PROCEDURE sp_info_pais (
    p_id_seleccion      IN NUMBER,
    p_anio              IN NUMBER DEFAULT NULL,
    p_mostrar_detalles  IN VARCHAR2 DEFAULT 'S'
)
AS
BEGIN
    -- ... código del procedure ...
END sp_info_pais;
/
```

---

## 5. Configuración de Output

Para ver correctamente los resultados en SQL*Plus:

```sql
SET PAGESIZE 0
SET LINESIZE 200
SET LONG 20000
SET TRIMSPOOL ON
SET ECHO OFF
SET FEEDBACK OFF
SET HEADING OFF
```

---

## 6. Parámetros por Defecto

### P_ANIO
- **Obligatorio** para `sp_info_mundial`
- Años disponibles: 1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022

### P_ETAPA
Valores típicos: 'Grupo', 'Octavos de final', 'Cuartos de final', 'Semifinal', 'Tercer lugar', 'Final'

### P_ID_GRUPO
Valores típicos: A, B, C, D, E, F, G, H (depende del año)

---

## Notas Importantes

1. **NULL en parámetros opcionales = sin filtro**
   ```sql
   EXEC sp_info_mundial(2022, NULL, NULL, NULL);  -- Muestra TODO
   ```

2. **Los procedures usan DBMS_OUTPUT.PUT_LINE()**
   - Asegúrate de tener habilitado el output
   - En SQL Developer: Ver > Dbms Output

3. **Manejo de errores**
   - Si el año no existe, muestra mensaje de error
   - Si el país no existe, muestra mensaje de error
   - Los parámetros opcionales filtrán, no dan error

4. **Performance**
   - Los procedures optimizados para BD con ~2000 registros
   - Pueden tardar unos segundos en mundiales grandes

---

## Casos de Uso Típicos

```sql
-- Análisis de mundial específico
EXEC sp_info_mundial(2022);

-- Comparar desempeño de dos países en un año
EXEC sp_info_mundial(1986, NULL, 6);  -- Argentina 1986
EXEC sp_info_mundial(1986, NULL, 11); -- Brasil 1986

-- Historial completo de un país
EXEC sp_info_pais(34);  -- Historia de España

-- Análisis de desempeño agrupado
EXEC sp_info_pais(36, NULL, 'N');  -- Francia sin detalles
```

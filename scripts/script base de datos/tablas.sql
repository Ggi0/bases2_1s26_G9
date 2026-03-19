-- ============================================================
-- PROYECTO FASE 1 - Sistemas de Bases de Datos 2
-- Oracle 21c - Script 01: Creación de tablas
-- ============================================================

BEGIN
    FOR t IN (
        SELECT table_name FROM user_tables
        WHERE table_name IN (
            'EQUIPO_IDEAL','TARJETA','PREMIO','POSICION_FINAL',
            'GOLEADOR','GOL','POSICION_GRUPO','PARTIDO',
            'GRUPO','JUGADOR_PAIS','MUNDIAL','SELECCION'
        )
    ) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
END;
/

-- ============================================================
-- 1. SELECCION
-- ============================================================
CREATE TABLE SELECCION (
    ID_SELECCION    NUMBER          NOT NULL,
    NOMBRE          VARCHAR2(100)   NOT NULL,
    CONSTRAINT PK_SELECCION PRIMARY KEY (ID_SELECCION)
);

-- ============================================================
-- 2. JUGADOR_PAIS
-- ============================================================
CREATE TABLE JUGADOR_PAIS (
    ID_JUGADOR      NUMBER          NOT NULL,
    NOMBRE          VARCHAR2(200)   NOT NULL,
    ID_SELECCION    NUMBER          NOT NULL,
    SELECCION       VARCHAR2(100),
    CONSTRAINT PK_JUGADOR_PAIS PRIMARY KEY (ID_JUGADOR),
    CONSTRAINT FK_JUGADOR_SEL  FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION)
);

-- ============================================================
-- 3. MUNDIAL
-- ============================================================
CREATE TABLE MUNDIAL (
    ANIO                NUMBER(4)       NOT NULL,
    ID_ORGANIZADOR      NUMBER,
    ORGANIZADOR         VARCHAR2(100),
    ID_CAMPEON          NUMBER,
    CAMPEON             VARCHAR2(100),
    NUM_SELECCIONES     NUMBER,
    NUM_PARTIDOS        NUMBER,
    GOLES               NUMBER,
    PROMEDIO_GOL        NUMBER(5,2),
    CONSTRAINT PK_MUNDIAL     PRIMARY KEY (ANIO),
    CONSTRAINT FK_MUN_ORG     FOREIGN KEY (ID_ORGANIZADOR)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_MUN_CAMPEON FOREIGN KEY (ID_CAMPEON)
        REFERENCES SELECCION(ID_SELECCION)
);

-- ============================================================
-- 4. GRUPO
-- ============================================================
CREATE TABLE GRUPO (
    ID_GRUPO        NUMBER          NOT NULL,
    ANIO            NUMBER(4)       NOT NULL,
    NOMBRE          VARCHAR2(50)    NOT NULL,
    SELECCIONES     VARCHAR2(500),
    CONSTRAINT PK_GRUPO     PRIMARY KEY (ID_GRUPO),
    CONSTRAINT FK_GRUPO_MUN FOREIGN KEY (ANIO)
        REFERENCES MUNDIAL(ANIO)
);

-- ============================================================
-- 5. PARTIDO
-- ============================================================
CREATE TABLE PARTIDO (
    ID_PARTIDO          NUMBER          NOT NULL,
    ANIO                NUMBER(4)       NOT NULL,
    NUM_PARTIDO         NUMBER,
    FECHA               VARCHAR2(20),
    ETAPA               VARCHAR2(100),
    ID_LOCAL            NUMBER,
    LOCAL               VARCHAR2(100),
    ID_VISITANTE        NUMBER,
    VISITANTE           VARCHAR2(100),
    GOLES_LOCAL         NUMBER,
    GOLES_VISITANTE     NUMBER,
    TIEMPO_EXTRA        VARCHAR2(2),
    PENALES             VARCHAR2(2),
    PENALES_LOCAL       NUMBER,
    PENALES_VISITANTE   NUMBER,
    CONSTRAINT PK_PARTIDO       PRIMARY KEY (ID_PARTIDO),
    CONSTRAINT FK_PARTIDO_MUN   FOREIGN KEY (ANIO)
        REFERENCES MUNDIAL(ANIO),
    CONSTRAINT FK_PARTIDO_LOCAL FOREIGN KEY (ID_LOCAL)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_PARTIDO_VISIT FOREIGN KEY (ID_VISITANTE)
        REFERENCES SELECCION(ID_SELECCION)
);

-- ============================================================
-- 6. POSICION_GRUPO
-- ============================================================
CREATE TABLE POSICION_GRUPO (
    ID_POSICION_GRUPO   NUMBER      NOT NULL,
    ID_GRUPO            NUMBER      NOT NULL,
    ANIO                NUMBER(4),
    GRUPO               VARCHAR2(50),
    ID_SELECCION        NUMBER      NOT NULL,
    PAIS                VARCHAR2(100),
    PTS                 NUMBER,
    PJ                  NUMBER,
    PG                  NUMBER,
    PE                  NUMBER,
    PP                  NUMBER,
    GF                  NUMBER,
    GC                  NUMBER,
    DIFERENCIA          NUMBER,
    CLASIFICADO         VARCHAR2(5),
    CONSTRAINT PK_POSICION_GRUPO PRIMARY KEY (ID_POSICION_GRUPO),
    CONSTRAINT FK_POSGRP_GRUPO   FOREIGN KEY (ID_GRUPO)
        REFERENCES GRUPO(ID_GRUPO),
    CONSTRAINT FK_POSGRP_SEL     FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION)
);

-- ============================================================
-- 7. GOL (ID_JUGADOR nullable → se llena si el jugador existe)
-- ============================================================
CREATE TABLE GOL (
    ID_GOL          NUMBER      NOT NULL,
    ID_PARTIDO      NUMBER      NOT NULL,
    ANIO            NUMBER(4),
    NUM_PARTIDO     NUMBER,
    FECHA           VARCHAR2(20),
    ID_SELECCION    NUMBER,
    EQUIPO          VARCHAR2(100),
    ID_JUGADOR      NUMBER,
    JUGADOR         VARCHAR2(200),
    MINUTO          NUMBER,
    ES_PENAL        VARCHAR2(2),
    CONSTRAINT PK_GOL         PRIMARY KEY (ID_GOL),
    CONSTRAINT FK_GOL_PARTIDO FOREIGN KEY (ID_PARTIDO)
        REFERENCES PARTIDO(ID_PARTIDO),
    CONSTRAINT FK_GOL_SEL     FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_GOL_JUG     FOREIGN KEY (ID_JUGADOR)
        REFERENCES JUGADOR_PAIS(ID_JUGADOR)
);

-- ============================================================
-- 8. GOLEADOR (ID_JUGADOR nullable)
-- ============================================================
CREATE TABLE GOLEADOR (
    ID_GOLEADOR     NUMBER          NOT NULL,
    ANIO            NUMBER(4),
    ID_SELECCION    NUMBER,
    PAIS            VARCHAR2(100),
    ID_JUGADOR      NUMBER,
    JUGADOR         VARCHAR2(200),
    GOLES           NUMBER,
    PARTIDOS        NUMBER,
    PROMEDIO        NUMBER(5,2),
    CONSTRAINT PK_GOLEADOR     PRIMARY KEY (ID_GOLEADOR),
    CONSTRAINT FK_GOLEADOR_SEL FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_GOLEADOR_JUG FOREIGN KEY (ID_JUGADOR)
        REFERENCES JUGADOR_PAIS(ID_JUGADOR)
);

-- ============================================================
-- 9. POSICION_FINAL
-- ============================================================
CREATE TABLE POSICION_FINAL (
    ID_POSICION_FINAL   NUMBER      NOT NULL,
    ANIO                NUMBER(4),
    POSICION            NUMBER,
    ID_SELECCION        NUMBER,
    PAIS                VARCHAR2(100),
    CONSTRAINT PK_POSICION_FINAL PRIMARY KEY (ID_POSICION_FINAL),
    CONSTRAINT FK_POSFIN_SEL     FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION)
);

-- ============================================================
-- 10. PREMIO (ID_JUGADOR nullable)
-- ============================================================
CREATE TABLE PREMIO (
    ID_PREMIO       NUMBER          NOT NULL,
    ANIO            NUMBER(4),
    TIPO_PREMIO     VARCHAR2(100),
    ID_JUGADOR      NUMBER,
    JUGADOR         VARCHAR2(200),
    ID_SELECCION    NUMBER,
    PAIS            VARCHAR2(100),
    CONSTRAINT PK_PREMIO     PRIMARY KEY (ID_PREMIO),
    CONSTRAINT FK_PREMIO_SEL FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_PREMIO_JUG FOREIGN KEY (ID_JUGADOR)
        REFERENCES JUGADOR_PAIS(ID_JUGADOR)
);

-- ============================================================
-- 11. EQUIPO_IDEAL (ID_JUGADOR nullable)
-- ============================================================
CREATE TABLE EQUIPO_IDEAL (
    ID_EQUIPO_IDEAL NUMBER          NOT NULL,
    ANIO            NUMBER(4),
    POSICION        VARCHAR2(50),
    ID_JUGADOR      NUMBER,
    JUGADOR         VARCHAR2(200),
    ID_SELECCION    NUMBER,
    PAIS            VARCHAR2(100),
    CONSTRAINT PK_EQUIPO_IDEAL     PRIMARY KEY (ID_EQUIPO_IDEAL),
    CONSTRAINT FK_EQUIPO_IDEAL_SEL FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_EQUIPO_IDEAL_JUG FOREIGN KEY (ID_JUGADOR)
        REFERENCES JUGADOR_PAIS(ID_JUGADOR)
);

-- ============================================================
-- 12. TARJETA (ID_JUGADOR nullable)
-- ============================================================
CREATE TABLE TARJETA (
    ID_TARJETA      NUMBER          NOT NULL,
    ANIO            NUMBER(4),
    ID_SELECCION    NUMBER,
    PAIS            VARCHAR2(100),
    ID_JUGADOR      NUMBER,
    JUGADOR         VARCHAR2(200),
    AMARILLAS       NUMBER,
    ROJAS           NUMBER,
    CONSTRAINT PK_TARJETA     PRIMARY KEY (ID_TARJETA),
    CONSTRAINT FK_TARJETA_SEL FOREIGN KEY (ID_SELECCION)
        REFERENCES SELECCION(ID_SELECCION),
    CONSTRAINT FK_TARJETA_JUG FOREIGN KEY (ID_JUGADOR)
        REFERENCES JUGADOR_PAIS(ID_JUGADOR)
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IDX_PARTIDO_ANIO    ON PARTIDO(ANIO);
CREATE INDEX IDX_PARTIDO_LOCAL   ON PARTIDO(ID_LOCAL);
CREATE INDEX IDX_PARTIDO_VISIT   ON PARTIDO(ID_VISITANTE);
CREATE INDEX IDX_GOL_PARTIDO     ON GOL(ID_PARTIDO);
CREATE INDEX IDX_GOL_SEL         ON GOL(ID_SELECCION);
CREATE INDEX IDX_GOL_JUG         ON GOL(ID_JUGADOR);
CREATE INDEX IDX_POSGRP_GRUPO    ON POSICION_GRUPO(ID_GRUPO);
CREATE INDEX IDX_POSGRP_SEL      ON POSICION_GRUPO(ID_SELECCION);
CREATE INDEX IDX_GOLEADOR_ANIO   ON GOLEADOR(ANIO);
CREATE INDEX IDX_GOLEADOR_JUG    ON GOLEADOR(ID_JUGADOR);
CREATE INDEX IDX_TARJETA_ANIO    ON TARJETA(ANIO);
CREATE INDEX IDX_TARJETA_JUG     ON TARJETA(ID_JUGADOR);
CREATE INDEX IDX_JUGADOR_SEL     ON JUGADOR_PAIS(ID_SELECCION);
CREATE INDEX IDX_JUGADOR_NOMBRE  ON JUGADOR_PAIS(NOMBRE);

COMMIT;

SELECT TABLE_NAME FROM USER_TABLES
WHERE TABLE_NAME IN (
    'SELECCION','JUGADOR_PAIS','MUNDIAL','GRUPO','PARTIDO',
    'POSICION_GRUPO','GOL','GOLEADOR','POSICION_FINAL',
    'PREMIO','EQUIPO_IDEAL','TARJETA'
)
ORDER BY TABLE_NAME;
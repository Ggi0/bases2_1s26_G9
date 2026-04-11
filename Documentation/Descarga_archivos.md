## Documentación técnica

**Script:** `scripts/desactualizados/descarga.py`
**Lenguaje:** Python

---

## 1. Descripción general

Este script implementa un proceso de **web scraping automatizado** para descargar el contenido HTML de páginas web asociadas a selecciones nacionales de fútbol.

El objetivo principal es recorrer una lista predefinida de URLs y almacenar localmente el HTML completo de cada página, tal como es renderizado por un navegador real. Esto permite trabajar posteriormente con datos estructurados sin depender de la disponibilidad del sitio web.

A diferencia de un scraping básico con librerías como `requests`, este script utiliza un navegador real para garantizar que el contenido dinámico sea cargado correctamente.

---

## 2. Tecnologías utilizadas

* **Python**: lenguaje principal para la automatización del proceso.
* **Selenium**: framework que permite controlar navegadores de forma programática.
* **Mozilla Firefox**: navegador utilizado para ejecutar las peticiones.
* **Geckodriver**: intermediario entre Selenium y Firefox.

### Instalación de dependencias

Para el correcto funcionamiento del script es necesario instalar `geckodriver`, que permite a Selenium controlar Firefox:

```bash
sudo port install geckodriver
```

Además, se debe contar con Firefox instalado en el sistema.

---

## 3. ¿Qué es Selenium y cómo funciona?

Selenium es una herramienta de automatización de navegadores que permite simular la interacción de un usuario con páginas web. Internamente, funciona mediante un **WebDriver**, que actúa como intermediario entre el código Python y el navegador.

En este caso, Selenium utiliza Geckodriver para enviar instrucciones a Firefox, tales como abrir una URL, esperar la carga del contenido y obtener el HTML renderizado. Esto es especialmente útil cuando las páginas dependen de JavaScript, ya que el navegador ejecuta el código y genera el DOM final antes de ser capturado.

---

## 4. Estructura del script

El script está dividido en las siguientes secciones principales:

### 4.1. Definición de constantes

```python
HTML_DIR = "html"
```

* Define el directorio donde se almacenarán los archivos descargados.

```python
URLS_SELECCIONES = [ ... ]
```

* Lista estática de URLs correspondientes a distintas selecciones nacionales.
* Cada URL apunta a una página específica con información de jugadores.

---

### 4.2. Creación del driver

```python
def crear_driver():
```

* Inicializa una instancia de Firefox controlada por Selenium.
* Configura opciones del navegador mediante `Options()`.

Características:

* Permite ejecutar en modo **headless** (sin interfaz gráfica), aunque está desactivado por defecto.
* Retorna un objeto `driver` que se utiliza para interactuar con las páginas.

---

### 4.3. Proceso de descarga

```python
def descargar_paginas():
```

Esta es la función principal del script y realiza las siguientes operaciones:

#### a. Preparación del entorno

* Crea la carpeta `html/` si no existe.
* Calcula el total de URLs.

#### b. Reanudación de descargas

* Verifica qué archivos ya existen en disco.
* Omite aquellos que ya fueron descargados previamente.
* Genera una lista de URLs pendientes.

Esto permite continuar el proceso si fue interrumpido.

#### c. Inicialización del navegador

* Llama a `crear_driver()` para abrir Firefox.

#### d. Iteración sobre URLs

Para cada URL pendiente:

1. Navega a la página:

   ```python
   driver.get(url)
   ```

2. Espera la carga completa:

   ```python
   time.sleep(3)
   ```

3. Obtiene el HTML renderizado:

   ```python
   html = driver.page_source
   ```

4. Valida el tamaño del contenido:

   * Si es menor a 500 caracteres, muestra advertencia.

5. Guarda el contenido en un archivo:

   ```python
   with open(ruta_destino, "w", encoding="utf-8") as f:
       f.write(html)
   ```

#### e. Control de carga

* Introduce un retraso aleatorio entre 10 y 20 segundos:

  ```python
  random.randint(10, 20)
  ```
* Esto reduce la probabilidad de bloqueo por parte del servidor.

#### f. Manejo de errores

* Captura excepciones individuales por URL.
* Permite continuar el proceso sin detener toda la ejecución.

#### g. Cierre del navegador

* Se garantiza el cierre de Firefox mediante un bloque `finally`:

  ```python
  driver.quit()
  ```

---

### 4.4. Punto de entrada

```python
if __name__ == "__main__":
```

* Ejecuta el script directamente.
* Muestra información inicial:

  * Total de selecciones
  * Advertencia sobre el uso del navegador
* Llama a `descargar_paginas()`.

---

## 5. Flujo de ejecución

1. Se inicia el script.
2. Se imprime el total de URLs.
3. Se crea la carpeta de salida si no existe.
4. Se filtran archivos ya descargados.
5. Se abre Firefox mediante Selenium.
6. Para cada URL pendiente:

   * Se navega a la página.
   * Se espera la carga.
   * Se obtiene el HTML.
   * Se guarda en disco.
   * Se espera un tiempo aleatorio.
7. Se cierra el navegador.
8. Finaliza el proceso.

---

## 6. Resultado esperado

* Se genera una carpeta `html/`.
* Dentro de ella, se almacenan archivos `.html`, uno por cada selección.
* Cada archivo contiene el HTML completo renderizado por el navegador.

---

## 7. Consideraciones

* El uso de delays es importante para evitar bloqueos.
* El script depende de la estructura actual del sitio web.
* Puede requerir mantenimiento si cambian las URLs o el contenido.
* El modo headless puede activarse para ejecución en servidores.

---
## 10. Propósito dentro del proyecto

* capturas de images de la forma en que se extrajo la inforación de pagina:

![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.43.20.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.43.58.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.45.52.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.47.32.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.48.24.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.48.53.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.49.14.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.50.18.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.53.42.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.54.06.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.54.31.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.56.57.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.57.44.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 22.59.17.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.00.12.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.01.48.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.03.17.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.03.48.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.04.08.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.04.45.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.05.40.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.07.07.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.07.48.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.08.16.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.09.09.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.10.06.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.10.50.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.11.13.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.12.25.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.12.47.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.13.46.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.15.08.png>) 

---
## 9. Propósito dentro del proyecto

Este script cumple la función de **fase de adquisición de datos**, permitiendo obtener una copia local de las páginas web. Posteriormente, estos archivos pueden ser procesados por otros componentes del sistema (por ejemplo, parsers o pipelines de datos).


## Documentación técnica

**Script:** `descarga_mundial.py`
**Lenguaje:** Python

---

## 1. Descripción general

Este script implementa un proceso de **web scraping automatizado orientado a eventos**, específicamente para descargar toda la información asociada a un mundial de fútbol desde un sitio web.

A diferencia de un scraping basado en listas estáticas de URLs, este script **descubre dinámicamente las páginas relevantes** de cada mundial a partir de una página principal, lo que lo hace más flexible y mantenible.

El resultado final es un conjunto de archivos HTML organizados por año, que contienen el contenido completo renderizado de cada sección del mundial (grupos, resultados, goleadores, entre otros).

---

## 2. Tecnologías utilizadas

* **Python**: lenguaje principal para la automatización.
* **Selenium**: permite controlar un navegador real para evitar bloqueos del servidor (HTTP 403).
* **Mozilla Firefox**: navegador utilizado para ejecutar las solicitudes.
* **Geckodriver**: puente entre Selenium y Firefox.
* **Beautiful Soup**: librería para parsear y extraer enlaces del HTML.

### Instalación de dependencias

```bash
pip install selenium beautifulsoup4 pandas
brew install geckodriver
```

---

## 3. ¿Qué es Selenium y cómo funciona?

Selenium es un framework de automatización que permite controlar navegadores web mediante código. En este caso, se utiliza para abrir páginas web con un navegador real y obtener el HTML completamente renderizado, incluyendo contenido generado dinámicamente por JavaScript.

El flujo es el siguiente:

1. Selenium envía instrucciones al WebDriver.
2. Geckodriver traduce esas instrucciones para Firefox.
3. Firefox ejecuta la navegación como si fuera un usuario real.
4. El script obtiene el HTML final mediante `page_source`.

Esto permite evitar restricciones del servidor que bloquean peticiones automatizadas tradicionales.

---

## 4. Estructura del script

El script está organizado en módulos funcionales que representan cada etapa del proceso.

---

### 4.1. Configuración base

```python
BASE_URL = "https://www.losmundialesdefutbol.com/"
```

* Define la URL base del sitio web.
* Se utiliza para construir URLs absolutas mediante `urljoin`.

---

### 4.2. Creación del driver

```python
def crear_driver(headless=False):
```

* Inicializa el navegador Firefox controlado por Selenium.
* Permite dos modos:

  * **headless=True**: ejecución en segundo plano (sin interfaz gráfica).
  * **headless=False**: ejecución visible para monitoreo.

---

### 4.3. Generación de nombres de archivo

```python
def nombre_archivo(url):
```

* Convierte una URL en un nombre de archivo `.html`.
* Ejemplo:

  ```
  /mundiales/1930_grupo_1.php → 1930_grupo_1.html
  ```

---

### 4.4. Descubrimiento de enlaces

```python
def descubrir_links_mundial(driver, anio):
```

Esta función es clave para la automatización dinámica del scraping.

#### Proceso:

1. Construye la URL principal del mundial:

   ```
   /mundiales/{anio}_mundial.php
   ```

2. Navega a la página usando Selenium.

3. Obtiene el HTML renderizado.

4. Parsea el contenido con Beautiful Soup.

5. Extrae todos los enlaces (`<a href="">`).

6. Filtra los enlaces relevantes:

   * Deben pertenecer al mismo mundial (`/{anio}_`).
   * Deben estar dentro de `/mundiales/`.
   * Se excluyen páginas de partidos (`/partidos/`).
   * Se evita duplicar la página principal.

7. Elimina duplicados manteniendo el orden original.

#### Resultado:

* Lista de URLs únicas que representan todas las páginas relevantes del mundial.

---

### 4.5. Descarga de páginas

```python
def descargar_mundial(anio):
```

Función principal que ejecuta el flujo completo de descarga para un mundial específico.

#### a. Preparación

* Crea el directorio:

  ```
  html/{anio}/
  ```

#### b. Inicialización

* Abre Firefox mediante Selenium.

#### c. Descubrimiento de enlaces

* Llama a `descubrir_links_mundial()`.

#### d. Reanudación de descargas

* Verifica qué archivos ya existen.
* Omite los ya descargados.
* Genera lista de pendientes.

#### e. Descarga secuencial

Para cada URL pendiente:

1. Navega a la página:

   ```python
   driver.get(url)
   ```

2. Espera la carga completa:

   ```python
   time.sleep(3)
   ```

3. Obtiene el HTML:

   ```python
   html = driver.page_source
   ```

4. Valida el tamaño:

   * Si es menor a 500 caracteres, muestra advertencia.

5. Guarda el archivo en disco:

   ```python
   with open(ruta, "w", encoding="utf-8") as f:
       f.write(html)
   ```

#### f. Control de carga

* Introduce un retraso aleatorio entre 40 y 60 segundos.
* Reduce la probabilidad de bloqueo por parte del servidor.

#### g. Manejo de errores

* Captura excepciones individuales.
* Permite continuar el proceso.

#### h. Cierre del navegador

* Garantiza el cierre con `driver.quit()`.

---

### 4.6. Punto de entrada

```python
if __name__ == "__main__":
```

Permite ejecutar el script desde línea de comandos.

#### Comportamiento:

* Si se proporcionan argumentos:

  ```bash
  python descarga_mundial.py 1930 1934
  ```

  → descarga múltiples mundiales.

* Si no se proporcionan argumentos:

  ```bash
  python descarga_mundial.py
  ```

  → descarga el mundial 1930 por defecto.

---

## 5. Flujo de ejecución

1. Se leen los años desde la línea de comandos.
2. Para cada año:

   * Se crea el directorio correspondiente.
   * Se abre Firefox.
   * Se descubren los enlaces del mundial.
   * Se filtran los ya descargados.
   * Se descargan los pendientes:

     * Navegación
     * Espera
     * Extracción de HTML
     * Guardado
     * Delay aleatorio
   * Se cierra el navegador.
3. Finaliza el proceso.

---

## 6. Resultado esperado

Estructura de salida:

```
html/
 ├── 1930/
 │    ├── 1930_mundial.html
 │    ├── 1930_grupo_1.html
 │    ├── 1930_final.html
 │    └── ...
 ├── 1934/
 │    └── ...
```

Cada archivo contiene el HTML completo de una sección del mundial.

---

## 7. Consideraciones técnicas

* El scraping depende de la estructura actual del sitio web.
* El uso de Selenium es necesario para evitar bloqueos HTTP 403.
* Los delays son fundamentales para evitar restricciones del servidor.
* El script es tolerante a fallos y permite reanudación.
* Puede ejecutarse en modo headless para entornos sin interfaz gráfica.

---
![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.17.36.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.18.47.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.19.54.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.20.46.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.21.37.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.22.22.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.25.39.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.26.35.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.27.12.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.28.35.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.29.51.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.31.01.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.33.26.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.34.30.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.36.46.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.38.00.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.40.44.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.41.49.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.42.47.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.43.22.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.47.00.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.54.03.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.54.39.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.55.41.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.56.39.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.57.19.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.58.17.png>) ![alt text](<../images/descarga/Captura de Pantalla 2026-04-10 a la(s) 23.59.17.png>)


---
## 9. Propósito dentro del proyecto

Este script forma parte de la **fase de adquisición de datos**, permitiendo recolectar de forma estructurada toda la información de cada mundial.

A diferencia de scripts basados en listas fijas, este enfoque permite adaptarse automáticamente a nuevas páginas dentro de cada mundial, facilitando el mantenimiento y escalabilidad del sistema.

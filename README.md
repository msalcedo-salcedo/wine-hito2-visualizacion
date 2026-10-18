# Hito 2 · Wine: perfiles químicos y contexto vitivinícola

Visualización de Datos, UPeU · Grupo 3 · 18 de octubre de 2026.

## Entrega y ejecución

El proyecto continúa el Hito1 Wine: tres cultivares, 178 muestras, 13 mediciones, seis KPI, decisiones D1–D5, preguntas Q1–Q6 y wireframe A. El notebook añade Q7–Q10, diez visualizaciones interpretadas, incertidumbre y un panel declarativo de cuatro vistas conectadas. La app Streamlit tiene una página de laboratorio con cuatro gráficos conectados por filtros y otra página de contexto con mapa y serie anual.

El mapa SVG conserva los polígonos GeoJSON originales y permite consultar país, volumen y variación mediante tooltips. Usa proyección equirectangular identificada y datos locales; no depende de servicios de mapas ni de librerías JavaScript externas. El panel Altair HTML sí carga sus librerías desde CDN.

Python 3.12 recomendado. Desde esta carpeta:

```bash
python -m pip install -r requirements.txt
python pruebas.py
python -m streamlit run app.py
```

Abra `Hito2_Wine.ipynb` con Jupyter/VS Code y ejecute todas las celdas. Para instalar la interfaz de Jupyter, opcionalmente `python -m pip install jupyterlab`. Las figuras estáticas se pueden regenerar con `python figuras_estaticas.py`. El panel `Panel_4_vistas.html` se abre en un navegador con conexión a Internet para cargar Vega/Vega-Lite/Vega-Embed desde CDN; el resto del cálculo usa datos locales. La app no necesita servicios AWS, claves ni bases externas.

## Archivos

- `app.py`: aplicación Streamlit; entrada para Community Cloud.
- `analisis.py`: carga, filtros, KPI, bootstrap, gráficos Plotly/Altair compartidos.
- `Hito2_Wine.ipynb`: cuaderno con datos, cálculos, diez gráficos, lectura y límites.
- `figuras_estaticas.py`: gráficos para notebook y PDF.
- `pruebas.py`: verificaciones analíticas y Streamlit AppTest.
- `data/`: Wine original, OIV transcrito, polígonos y procedencia.
- `docs/`: decisiones y wireframe del Hito1, interpretaciones del Hito2.
- `evidencias/`: resultados de pruebas y capturas de verificación.

## Indicadores y filtros

Laboratorio: n válido; completitud de filas; duplicados adicionales; balance mínimo/máximo n; media de alcohol; mayor η². Filtros de cultivar múltiple y rango de alcohol actualizan todos los KPI y cuatro vistas: cobertura, relación alcohol/color, flavonoides e IC de la media. El denominador de completitud/duplicados son filas del alcance. Balance cuenta los grupos seleccionados aunque queden vacíos, y no aplica con menos de dos grupos seleccionados. η² no aplica con menos de dos grupos observados. Un alcance vacío muestra aviso, sin estimaciones ficticias.

Contexto: producción mundial, cobertura de diez países y año comparado. Filtro de año para mapa (2016–2024) y selección de países en serie (2015–2024). Mapa SVG con polígonos locales Natural Earth y proyección equirectangular; cambio anual porcentual, escala fija ±30% centrada en cero; gris significa fuera de cobertura. La figura impresa usa una proyección equirectangular identificada. La selección por región del panel HTML enlaza cuatro vistas adicionales.

## Fuentes y límites

1. UCI Machine Learning Repository, **Wine**, DOI 10.24432/C5PC7J, CC BY 4.0: https://archive.ics.uci.edu/dataset/109/wine . Se conservan `wine.data` y `wine.names` del Hito1; no se imputan fechas ni países.
2. OIV (2025, septiembre), **OIV Statistical Brief: Wine, Table Grapes & Dried Grapes in 2024**, tabla 15, p.14: https://www.oiv.int/sites/default/files/documents/OIV_Statistical_Brief-Wine_Table_Grapes_and_Dried_Grapes_in_2024_0.pdf . Transcripción de diez países + Otros + Mundo durante diez años. Producción excluye mostos y jugos; mhl = millones de hectolitros. Cifras redondeadas/revisables; el CSV no conserva cursivas de estimaciones del PDF.
3. Natural Earth, Admin 0 Countries 1:110m, dominio público: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/ . GeoJSON: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson . Correspondencia ADM0_A3 a ISO3 verificada para los diez países OIV.

Wine no contiene fechas ni ubicación por muestra. OIV es una extensión **contextual independiente**, de grano país–año, sin unión con Wine; el mapa no representa el origen de los cultivares y las series no explican diferencias químicas. Las clases no indican calidad comercial. Correlación, η² y PCA son exploratorios, no causalidad ni precisión de clasificación.

Bootstrap percentil: 5.000 remuestras dentro de cada cultivar; semilla 42 + índice de grupo. IC de la media del 95%, no dispersión individual. Si n<2 no se estima IC. No se corrige sesgo de selección ni comparaciones múltiples. Para predicción futura separar entrenamiento y evaluación.

## Coherencia del diseño

Se mantienen calidad/cobertura primero, relación central y distribuciones/precisión después, paleta `#7B1E3A`, `#087F8C`, `#91670C`, etiquetas y símbolos redundantes. La página separada de contexto declara el cambio de granularidad. Barras desde cero, ejes comunes en small multiples, escala simétrica de correlación y de tasa geográfica. Controles etiquetados y descarga de detalle. No se afirma certificación WCAG.

La versión del notebook en GitHub conserva todas las celdas y omite salidas pesadas. El informe, la copia ejecutada y las carpetas docs/evidencias forman parte del paquete del aula.

## Despliegue

Repositorio: https://github.com/msalcedo-salcedo/wine-hito2-visualizacion

Aplicación pública verificada: https://wine-hito2-medalit.streamlit.app/ . Entorno de publicación: Python 3.12.

Para desplegar en Streamlit Community Cloud: seleccionar este repositorio, rama `main`, archivo principal `app.py`, Python 3.12. No introducir secretos.

## Autoría

Grupo 3: Medalit Nieves Salcedo Rodriguez, Max Alejandro Huaranja Montaño y Miguel Alexander Alviry Zapata. Se utilizó asistencia de Codex para programación, documentación y validación; el grupo debe revisar y comprender la entrega antes de presentarla.

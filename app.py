"""Dashboard Hito 2: ejecutar con streamlit run app.py."""
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from analisis import *

st.set_page_config(page_title='Wine | Hito 2',page_icon='🍇',layout='wide')
st.title('Wine: perfiles químicos y contexto vitivinícola')
st.caption('Hito 2 · Visualización de Datos · Grupo 3 · Continuidad del wireframe A del Hito 1')
page=st.radio('Área de análisis',['Laboratorio Wine','Contexto geográfico y temporal'],horizontal=True)
if page=='Laboratorio Wine':
    full=load_wine()
    st.write('Compare tres cultivares y explore mediciones antes de diseñar un clasificador. Las clases no indican calidad comercial.')
    a,b=st.columns([2,3])
    groups=a.multiselect('Cultivares',GROUPS,default=GROUPS)
    limits=b.slider('Rango de alcohol (escala original)',float(full.alcohol.min()),float(full.alcohol.max()),(float(full.alcohol.min()),float(full.alcohol.max())),step=.01)
    d=filter_wine(full,groups,limits)
    k=metrics(d,groups)
    band=st.columns(6)
    specs=[('Muestras válidas',k['n'],'178 en archivo'),('Completitud',k['completeness'],'% filas válidas'),('Duplicados',k['duplicates'],'% filas adicionales'),('Balance',k['balance'],'% mínimo/máximo'),('Media alcohol',k['alcohol'],'escala original'),('Mayor η²',k['max_eta'],'razón descriptiva')]
    for col,(label,value,note) in zip(band,specs):
        text=str(value) if label=='Muestras válidas' else f'{value:.3f}' if label in ['Media alcohol','Mayor η²'] else f'{value:.1f}%'
        col.metric(label,'No aplica' if isinstance(value,float) and not np.isfinite(value) else text);col.caption(note)
    st.caption(f'Alcance activo: {len(d)} de 178 muestras. Los filtros actualizan los seis KPI y las cuatro vistas. Doble clic en el gráfico restablece el zoom; los filtros superiores definen el alcance.')
    if d.empty:
        st.info('No hay muestras con estos filtros. Amplíe el rango de alcohol o seleccione otro cultivar.')
    else:
        left,right=st.columns(2)
        with left:
            st.plotly_chart(chart_counts(d,groups),use_container_width=True,key='counts')
            st.plotly_chart(chart_box(d),use_container_width=True,key='box')
        with right:
            st.plotly_chart(chart_scatter(d),use_container_width=True,key='scatter')
            st.plotly_chart(chart_ci(d),use_container_width=True,key='ci')
        st.caption('Cajas: dispersión individual. IC: incertidumbre de la media, bootstrap percentil 95%, 5.000 remuestras por grupo; semilla 42 + índice de cultivar. Si n<2 no se estima IC. Los filtros condicionan las estimaciones; no son inferencia confirmatoria.')
        with st.expander('Interpretación y decisiones'):
            st.write('Los flavonoides ayudan a contrastar perfiles; alcohol y color permiten revisar solapamientos. Compare primero n y dispersión, luego la precisión de medias. Un η² alto describe separación de medias en esta muestra; no demuestra exactitud futura ni causalidad.')
            st.dataframe(bootstrap_ci(d),hide_index=True,width='stretch')
            st.write('Balance conserva los cultivares seleccionados, incluso si un grupo queda con cero muestras. No aplica con menos de dos cultivares. La completitud y duplicación usan como denominador las filas del alcance.')
        with st.expander('Detalle de la selección'):
            st.dataframe(d,hide_index=True,width='stretch')
        st.download_button('Descargar muestras filtradas (CSV)',d.to_csv(index=False).encode('utf-8'),file_name='wine_seleccion.csv',mime='text/csv')
else:
    oiv=load_oiv()
    st.info('Fuente complementaria OIV: país–año. No representa la ubicación ni la fecha de las 178 muestras Wine. No se unen ambas tablas ni se transfieren conclusiones entre escalas.')
    a,b=st.columns(2)
    year=a.selectbox('Año del mapa',list(range(2016,2025)),index=8)
    countries=b.multiselect('Países en la serie',list(oiv[oiv.iso3!=''].pais.unique()),default=['Italia','Francia','España'])
    geo=geo_data(oiv,year)
    world=oiv[(oiv.pais=='Mundo')&(oiv.anio==year)].produccion_mhl.iloc[0]
    c1,c2,c3=st.columns(3)
    c1.metric('Producción mundial',f'{world:.1f} mhl')
    c2.metric('Cobertura de los 10 países',f'{100*geo.produccion_mhl.sum()/world:.1f}%')
    c3.metric('Año comparado',f'{year-1} → {year}')
    components.html(chart_map_html(oiv,year),height=490,scrolling=False)
    st.caption('Coropleta de variación relativa con escala divergente fija ±30% centrada en cero; gris = países fuera de la tabla, no producción cero. Mhl = millones de hectolitros. Los valores del tooltip conservan la tasa sin recorte; la escala se satura fuera de ±30%.')
    if countries: st.plotly_chart(chart_time(oiv,countries),use_container_width=True)
    else: st.info('Seleccione al menos un país para mostrar la serie.')
    st.write('En 2024 Italia crece frente a 2023 y Francia disminuye. La posición relativa cambia entre años: un único corte no resume toda la trayectoria. La serie no permite atribuir causas al clima o a la composición química.')
    with st.expander('Tabla y procedencia'):
        st.dataframe(geo,hide_index=True,width='stretch')
        st.write('Transcripción de OIV (septiembre de 2025), tabla 15, p.14: cifras redondeadas a 0,1 mhl; estimaciones y revisiones según la fuente. Datos 2015–2024, diez productores principales, agregado otros y mundo; no es una base de todos los países.')
st.divider()
st.caption('Fuentes: UCI Wine (CC BY 4.0) y OIV Statistical Brief, septiembre 2025, tabla 15. Las cifras OIV publicadas pueden revisarse.')
st.markdown('[UCI Wine](https://archive.ics.uci.edu/dataset/109/wine) · [Informe OIV](https://www.oiv.int/sites/default/files/documents/OIV_Statistical_Brief-Wine_Table_Grapes_and_Dried_Grapes_in_2024_0.pdf)')


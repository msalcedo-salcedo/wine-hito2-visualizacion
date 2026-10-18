"""Validación analítica y de interacciones; ejecutar python pruebas.py."""
import json
import numpy as np
from analisis import *

def run():
    d=load_wine();o=load_oiv();k=metrics(d)
    assert d.shape==(178,16)
    assert d.cultivar.value_counts().reindex(GROUPS).tolist()==[59,71,48]
    assert k['completeness']==100 and k['duplicates']==0 and k['n']==178
    assert np.isclose(k['alcohol'],13.00061797752809)
    assert eta_squared(d).index[0]=='flavonoides'
    assert .727<k['max_eta']<.729
    assert bootstrap_ci(d).equals(bootstrap_ci(d))
    ci=bootstrap_ci(d);assert (ci.inferior<=ci.media).all() and (ci.media<=ci.superior).all()
    one=filter_wine(d,[GROUPS[0]]);assert len(one)==59 and np.isnan(metrics(one,[GROUPS[0]])['balance']) and np.isnan(metrics(one)['max_eta'])
    empty=filter_wine(d,[],(0,1));assert len(empty)==0 and metrics(empty)['n']==0
    assert np.isnan(bootstrap_ci(d.iloc[:1]).inferior.iloc[0])
    assert metrics(d[d.clase==1],GROUPS)['balance']==0
    assert len(o)==120 and not o.duplicated(['pais','anio']).any()
    assert len(geo_data(o))==10 and geo_data(o).iso3.nunique()==10
    assert np.isclose(geo_data(o).set_index('iso3').loc['ITA','cambio_pct'],100*(44.1/38.3-1))
    for year in range(2015,2025):
        g=o[o.anio==year];assert abs(g[g.pais!='Mundo'].produccion_mhl.sum()-g[g.pais=='Mundo'].produccion_mhl.iloc[0])<=.31
    for f in [chart_counts,chart_scatter,chart_box,chart_ci,chart_eta,chart_ecdf,chart_corr,chart_pca]: assert len(f(d).data)>0
    assert len(chart_map(o).data)>0 and len(chart_time(o,['Italia']).data)==1
    assert chart_map_altair(o).to_dict()['projection']['type']=='equalEarth'
    spec=linked_panel(d).to_dict();assert len(spec['vconcat'])==2
    # Semantic AppTest executes both pages, filters, and empty cases.
    from streamlit.testing.v1 import AppTest
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=40).run()
    assert not at.exception, str(at.exception)
    assert len(at.metric)==6 and at.metric[0].value=='178'
    at.multiselect[0].set_value([GROUPS[0]]).run();assert not at.exception and at.metric[0].value=='59'
    at.multiselect[0].set_value([]).run();assert not at.exception and len(at.info)>0
    at.radio[0].set_value('Contexto geográfico y temporal').run();assert not at.exception and len(at.metric)==3
    at.selectbox[0].set_value(2016).run();assert not at.exception
    at.multiselect[0].set_value([]).run();assert not at.exception and len(at.info)>=2
    result={'estado':'APROBADO','alcances':['Datos Wine y OIV','KPI y bootstrap reproducible','Filtros vacío, un cultivar y grupo sin muestras','10 figuras Plotly y panel Altair válido','Streamlit: dos páginas, filtros, año y selección vacía'],'versiones':{}}
    import importlib.metadata
    for p in ['streamlit','plotly','altair','numpy','pandas','matplotlib','nbformat','nbclient']:result['versiones'][p]=importlib.metadata.version(p)
    (ROOT/'evidencias/pruebas.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': run()

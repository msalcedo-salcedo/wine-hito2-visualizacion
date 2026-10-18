"""Transformaciones y gráficos compartidos por notebook y Streamlit."""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
FEATURES = ['alcohol','acido_malico','cenizas','alcalinidad_cenizas','magnesio','fenoles_totales','flavonoides','fenoles_no_flavonoides','proantocianinas','intensidad_color','tonalidad','od280_od315','prolina']
GROUPS = ['Cultivar 1','Cultivar 2','Cultivar 3']
COLORS = dict(zip(GROUPS, ['#7B1E3A','#087F8C','#91670C']))
LABELS = {c:c.replace('_',' ').capitalize() for c in FEATURES}
LABELS.update(cultivar='Cultivar', id_muestra='Muestra', n='Muestras (n)', media='Media de alcohol', produccion_mhl='Producción (millones de hl)', anio='Año', pais='País', cambio_pct='Cambio interanual (%)')

def load_wine():
    df = pd.read_csv(ROOT/'data/wine.data', header=None, names=['clase']+FEATURES)
    df.insert(0, 'id_muestra', np.arange(1,len(df)+1))
    df['cultivar'] = df.clase.map({1:GROUPS[0],2:GROUPS[1],3:GROUPS[2]})
    return df

def filter_wine(df, groups, alcohol_range=None):
    mask = df.cultivar.isin(groups)
    if alcohol_range is not None:
        mask &= df.alcohol.between(*alcohol_range)
    return df.loc[mask].copy()

def eta_squared(df):
    if df.cultivar.nunique()<2 or df.empty:
        return pd.Series(dtype=float, name='eta2')
    out={}
    for c in FEATURES:
        total=((df[c]-df[c].mean())**2).sum()
        between=sum(len(g)*(g[c].mean()-df[c].mean())**2 for _,g in df.groupby('cultivar'))
        out[c]=between/total if total>0 else np.nan
    return pd.Series(out,name='eta2').dropna().sort_values(ascending=False)

def metrics(df, selected=GROUPS):
    n=len(df)
    valid=df[FEATURES].notna().all(axis=1)&np.isfinite(df[FEATURES]).all(axis=1)&df.clase.isin([1,2,3])
    counts=df.cultivar.value_counts().reindex(selected,fill_value=0)
    eta=eta_squared(df)
    return dict(n=int(valid.sum()), completeness=100*valid.mean() if n else np.nan,
        duplicates=100*df.duplicated(['clase']+FEATURES).mean() if n else np.nan,
        balance=100*counts.min()/counts.max() if len(counts)>=2 and counts.max()>0 else np.nan,
        alcohol=df.alcohol.mean(), max_eta=eta.max() if len(eta) else np.nan)

def bootstrap_ci(df, variable='alcohol', resamples=5000, seed=42):
    rows=[]
    for group,g in df.groupby('cultivar',sort=True):
        a=g[variable].dropna().to_numpy()
        if not len(a): continue
        # Separate deterministic generator for each class, stable across filters.
        rng=np.random.default_rng(seed+GROUPS.index(group))
        lo,hi=np.quantile(rng.choice(a,(resamples,len(a)),replace=True).mean(axis=1),[.025,.975]) if len(a)>=2 else (np.nan,np.nan)
        rows.append(dict(cultivar=group,n=len(a),media=a.mean(),inferior=lo,superior=hi))
    return pd.DataFrame(rows,columns=['cultivar','n','media','inferior','superior'])

def theme(fig, title):
    fig.update_layout(template='plotly_white',title=dict(text=title,font_size=18),font=dict(family='Arial',size=13,color='#292929'),margin=dict(l=45,r=20,t=65,b=50),legend_title_text='Cultivar',height=390)
    return fig

def chart_counts(df, selected=GROUPS):
    d=df.cultivar.value_counts().reindex(selected,fill_value=0).rename_axis('cultivar').reset_index(name='n')
    d['etiqueta']=[f'{n} ({n/len(df):.1%})' if len(df) else '0' for n in d.n]
    fig=px.bar(d,x='cultivar',y='n',color='cultivar',color_discrete_map=COLORS,text='etiqueta',labels=LABELS,category_orders={'cultivar':GROUPS})
    fig.update_yaxes(rangemode='tozero'); fig.update_layout(showlegend=False)
    return theme(fig,f'Cobertura por cultivar · n={len(df)}')

def chart_scatter(df, facets=False):
    fig=px.scatter(df,x='alcohol',y='intensidad_color',color='cultivar',symbol='cultivar',facet_col='cultivar' if facets else None,color_discrete_map=COLORS,labels=LABELS,hover_data=['id_muestra','flavonoides'],category_orders={'cultivar':GROUPS})
    return theme(fig,'Alcohol e intensidad de color · relación descriptiva')

def chart_box(df, variable='flavonoides'):
    fig=px.box(df,x='cultivar',y=variable,color='cultivar',points='outliers',color_discrete_map=COLORS,labels=LABELS,category_orders={'cultivar':GROUPS})
    fig.update_layout(showlegend=False)
    return theme(fig,f'Distribución de {LABELS[variable].lower()}')

def chart_ci(df):
    d=bootstrap_ci(df)
    fig=px.scatter(d,x='media',y='cultivar',color='cultivar',color_discrete_map=COLORS,error_x=d.superior-d.media,error_x_minus=d.media-d.inferior,hover_data=['n','inferior','superior'],labels=LABELS,category_orders={'cultivar':GROUPS})
    fig.update_traces(marker_size=11); fig.update_layout(showlegend=False)
    return theme(fig,'Media de alcohol e IC bootstrap del 95%')

def chart_eta(df):
    d=eta_squared(df).rename_axis('variable').reset_index()
    fig=px.bar(d.sort_values('eta2'),x='eta2',y='variable',orientation='h',labels={'eta2':'η² (razón 0–1)','variable':'Medición'})
    fig.update_traces(marker_color='#555555');fig.update_xaxes(range=[0,1]);fig.update_yaxes(ticktext=[LABELS[v] for v in d.sort_values('eta2').variable],tickvals=d.sort_values('eta2').variable)
    return theme(fig,'Separación descriptiva de medias · sin validación predictiva')

def chart_ecdf(df):
    return theme(px.ecdf(df,x='prolina',color='cultivar',line_dash='cultivar',color_discrete_map=COLORS,labels=LABELS),'Distribución acumulada de prolina')

def chart_corr(df):
    c=df[FEATURES].corr()
    fig=px.imshow(c,x=[LABELS[x] for x in c.columns],y=[LABELS[x] for x in c.index],zmin=-1,zmax=1,color_continuous_scale='RdBu_r',aspect='auto',labels={'color':'r de Pearson'})
    fig.update_layout(height=630)
    fig=theme(fig,'Correlación global · puede reflejar composición de cultivares');fig.update_layout(height=630)
    return fig

def pca_data(df):
    x=df[FEATURES].to_numpy(); z=(x-x.mean(axis=0))/x.std(axis=0,ddof=0)
    u,s,vt=np.linalg.svd(z,full_matrices=False)
    for i in range(len(s)):
        if vt[i,np.argmax(abs(vt[i]))]<0: u[:,i]*=-1;vt[i]*=-1
    d=df[['id_muestra','cultivar']].copy();d[['CP1','CP2']]=u[:,:2]*s[:2]
    return d,s*s/(s*s).sum()

def chart_pca(df):
    d,v=pca_data(df)
    return theme(px.scatter(d,x='CP1',y='CP2',color='cultivar',symbol='cultivar',color_discrete_map=COLORS,hover_data=['id_muestra'],labels={'CP1':f'CP1 ({v[0]:.1%})','CP2':f'CP2 ({v[1]:.1%})'}),'PCA de las 13 mediciones estandarizadas · exploratorio')

def load_oiv():
    return pd.read_csv(ROOT/'data/oiv_produccion_2015_2024.csv',keep_default_na=False)

def geo_data(oiv, year=2024):
    d=oiv[(oiv.anio==year)&(oiv.iso3!='')].copy()
    previous=oiv[(oiv.anio==year-1)&(oiv.iso3!='')].set_index('iso3').produccion_mhl
    d['anterior']=d.iso3.map(previous)
    d['cambio_pct']=100*(d.produccion_mhl/d.anterior-1)
    return d

def chart_map(oiv, year=2024):
    d=geo_data(oiv,year)
    fig=px.choropleth(d,locations='iso3',locationmode='ISO-3',color='cambio_pct',hover_name='pais',hover_data={'produccion_mhl':':.1f','cambio_pct':':+.1f','iso3':False},labels=LABELS,color_continuous_scale='RdBu',range_color=[-30,30],projection='natural earth')
    fig.update_geos(showcoastlines=False,showframe=False,landcolor='#e8e8e8')
    return theme(fig,f'Producción de vino · cambio {year-1}–{year} (%) · 10 países')

def chart_time(oiv, countries):
    d=oiv[oiv.pais.isin(countries)]
    fig=px.line(d,x='anio',y='produccion_mhl',color='pais',markers=True,labels=LABELS)
    fig.update_yaxes(rangemode='tozero');fig.update_xaxes(dtick=1)
    fig=theme(fig,'Producción anual de vino · contexto OIV 2015–2024')
    fig.update_layout(legend_title_text='País')
    return fig

def chart_map_html(oiv, year=2024):
    """Mapa SVG con proyección equirectangular y consulta nativa por país."""
    import json
    from html import escape
    features=json.loads((ROOT/'data/paises_natural_earth.geojson').read_text(encoding='utf-8'))['features']
    lookup=geo_data(oiv,year).set_index('iso3')
    parts=['<html><head><meta charset="utf-8"><style>body{margin:0;font:14px Arial;color:#292929}svg{width:100%;height:auto;max-height:470px}path:hover{stroke:#222;stroke-width:1.3px}path:focus{stroke:#111;stroke-width:2px;outline:none}</style></head><body>',
        f'<svg viewBox="0 0 1000 470" role="img" aria-label="Cambio porcentual de producción de vino {year-1} a {year}. Diez países. Proyección equirectangular."><text x="18" y="25" font-size="18" font-weight="bold">Cambio {year-1}–{year} · producción de vino (%)</text>']
    for f in features:
        props=f['properties'];iso=props['ADM0_A3']
        if iso=='ATA': continue
        if iso in lookup.index:
            row=lookup.loc[iso];value=float(row.cambio_pct);t=min(abs(value)/30,1)
            white=(247,247,247);end=(178,24,43) if value<0 else (33,102,172)
            color='#'+''.join(f'{round(a+(b-a)*t):02x}' for a,b in zip(white,end))
            label=f'{row.pais}: {row.produccion_mhl:.1f} mhl; cambio {value:+.1f}%'
        else:
            color='#dedede';label=f'{props["ADMIN"]}: fuera de cobertura OIV de esta tabla'
        geom=f['geometry'];polygons=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
        commands=[]
        for polygon in polygons:
            for ring in polygon:
                commands.append('M'+' L'.join(f'{18+(lon+180)*2.48:.2f},{45+(90-lat)*2.18:.2f}' for lon,lat,*_ in ring)+' Z')
        parts.append(f'<path data-iso="{escape(iso)}" tabindex="0" aria-label="{escape(label)}" d="{" ".join(commands)}" fill="{color}" fill-rule="evenodd" stroke="white" stroke-width=".35"><title>{escape(label)}</title></path>')
    parts.append('<defs><linearGradient id="escala"><stop offset="0%" stop-color="#b2182b"/><stop offset="50%" stop-color="#f7f7f7"/><stop offset="100%" stop-color="#2166ac"/></linearGradient></defs><rect x="640" y="405" width="260" height="15" fill="url(#escala)"/><text x="635" y="439">−30%</text><text x="761" y="439">0</text><text x="875" y="439">+30%</text><text x="18" y="407" font-size="12">Gris: fuera de cobertura. Pase el cursor sobre un país.</text><text x="18" y="429" font-size="12">Natural Earth 1:110m · Proyección equirectangular: áreas distorsionadas.</text><text x="18" y="451" font-size="12">OIV, tabla 15 (septiembre 2025). Escala saturada fuera de ±30%.</text></svg></body></html>')
    return ''.join(parts)

def linked_panel(df):
    """Cuatro vistas Altair conectadas por selección de cultivar y pincel."""
    import altair as alt
    groups=alt.selection_point(fields=['cultivar'],bind='legend',name='cultivares')
    brush=alt.selection_interval(encodings=['x','y'],name='rango_quimico')
    scale=alt.Scale(domain=GROUPS,range=list(COLORS.values()))
    base=alt.Chart(df).encode(color=alt.Color('cultivar:N',scale=scale,title='Cultivar'))
    scatter=base.mark_point(filled=True,size=65).encode(x=alt.X('alcohol:Q',scale=alt.Scale(zero=False),title='Alcohol'),y=alt.Y('intensidad_color:Q',title='Intensidad de color'),tooltip=['id_muestra','cultivar','alcohol','intensidad_color'],opacity=alt.condition(groups,alt.value(1),alt.value(.15))).add_params(groups,brush).properties(title='1. Seleccione una región; leyenda: cultivar',width=380,height=250)
    filtered=base.transform_filter(groups).transform_filter(brush)
    bars=filtered.mark_bar().encode(x=alt.X('cultivar:N',title='Cultivar'),y=alt.Y('count():Q',title='Muestras'),tooltip=['cultivar',alt.Tooltip('count():Q',title='n')]).properties(title='2. Cobertura seleccionada',width=380,height=250)
    box=filtered.mark_boxplot().encode(x=alt.X('cultivar:N',title='Cultivar'),y=alt.Y('flavonoides:Q',title='Flavonoides')).properties(title='3. Distribución seleccionada',width=380,height=250)
    # Explicit SE band here; bootstrap is chart 4 in notebook/app, separately labeled.
    dots=filtered.mark_circle(size=100).encode(x=alt.X('mean(alcohol):Q',title='Media de alcohol',scale=alt.Scale(zero=False)),y=alt.Y('cultivar:N',title='Cultivar'),tooltip=['cultivar',alt.Tooltip('mean(alcohol):Q',format='.3f'),alt.Tooltip('count():Q',title='n')]).properties(title='4. Media seleccionada',width=380,height=250)
    return alt.vconcat(alt.hconcat(scatter,bars),alt.hconcat(box,dots)).resolve_scale(color='shared').configure_view(stroke=None).configure(font='Arial')

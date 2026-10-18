"""Versiones para impresión; mismos datos, filtros y estimadores del dashboard."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import TwoSlopeNorm
from matplotlib.cm import ScalarMappable
from analisis import *

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':180,'axes.labelcolor':'#292929','text.color':'#292929'})

def static_chart(number,df=None,oiv=None):
    d=load_wine() if df is None else df
    o=load_oiv() if oiv is None else oiv
    fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained')
    if number==1:
        n=d.cultivar.value_counts().reindex(GROUPS,fill_value=0)
        ax.bar(GROUPS,n,color=list(COLORS.values()),width=.6)
        for i,v in enumerate(n):ax.text(i,v+1,f'{v} · {v/len(d):.1%}',ha='center')
        ax.set(ylabel='Muestras (n)',ylim=(0,n.max()*1.2),title='1 · Cobertura de tres cultivares')
    elif number==2:
        b=ax.boxplot([d[d.cultivar==g].flavonoides for g in GROUPS],tick_labels=GROUPS,patch_artist=True)
        for p,c in zip(b['boxes'],COLORS.values()):p.set(facecolor=c,alpha=.8)
        ax.set(ylabel='Flavonoides (escala original)',title='2 · Dispersión individual de flavonoides')
    elif number==3:
        plt.close(fig);fig,axes=plt.subplots(1,3,figsize=(10,3.8),sharex=True,sharey=True,layout='constrained')
        for ax,g in zip(axes,GROUPS):
            sub=d[d.cultivar==g];ax.scatter(sub.alcohol,sub.intensidad_color,c=COLORS[g],s=22);ax.set(title=f'{g} · n={len(sub)}',xlabel='Alcohol')
        axes[0].set_ylabel('Intensidad de color');fig.suptitle('3 · Alcohol y color: ejes comunes, paneles por cultivar')
    elif number==4:
        ci=bootstrap_ci(d)
        for i,r in ci.iterrows():
            ax.errorbar(r.media,i,xerr=[[r.media-r.inferior],[r.superior-r.media]],fmt='o',color=COLORS[r.cultivar],capsize=5)
            ax.text(r.superior+.02,i,f'n={r.n}',va='center',fontsize=9)
        ax.set(yticks=range(3),yticklabels=ci.cultivar,xlabel='Alcohol: media e IC bootstrap 95%',title='4 · Precisión de medias · 5.000 remuestras; semilla fija')
        ax.invert_yaxis();ax.margins(x=.15)
    elif number==5:
        e=eta_squared(d).sort_values();ax.barh([LABELS[v] for v in e.index],e,color='#555555')
        ax.set(xlim=(0,1),xlabel='η² (entre grupos / total)',title='5 · Separación de medias: ranking descriptivo')
    elif number==6:
        for g,ls in zip(GROUPS,['-','--',':']):
            v=np.sort(d[d.cultivar==g].prolina);ax.step(v,np.arange(1,len(v)+1)/len(v),where='post',label=g,color=COLORS[g],ls=ls,lw=2)
        ax.set(xlabel='Prolina (escala original)',ylabel='Proporción acumulada',title='6 · Distribución acumulada de prolina',ylim=(0,1.03));ax.legend()
    elif number==7:
        plt.close(fig);fig,ax=plt.subplots(figsize=(9,6.8),layout='constrained')
        c=d[FEATURES].corr();im=ax.imshow(c,vmin=-1,vmax=1,cmap='RdBu_r');fig.colorbar(im,ax=ax,label='r de Pearson')
        labels=[LABELS[v] for v in FEATURES];ax.set(xticks=range(13),yticks=range(13),yticklabels=labels,title='7 · Correlación global de mediciones')
        ax.set_xticklabels(labels,rotation=60,ha='right',fontsize=8);ax.tick_params(axis='y',labelsize=9)
    elif number==8:
        p,v=pca_data(d)
        for g,m in zip(GROUPS,['o','s','^']):
            sub=p[p.cultivar==g];ax.scatter(sub.CP1,sub.CP2,c=COLORS[g],label=g,marker=m,s=28)
        ax.set(xlabel=f'CP1 ({v[0]:.1%} varianza)',ylabel=f'CP2 ({v[1]:.1%} varianza)',title='8 · PCA de mediciones estandarizadas');ax.legend()
    elif number==9:
        geo=json.loads((ROOT/'data/paises_natural_earth.geojson').read_text(encoding='utf-8'))
        values=geo_data(o).set_index('iso3').cambio_pct.to_dict()
        norm=TwoSlopeNorm(vmin=-30,vcenter=0,vmax=30);cmap=plt.get_cmap('RdBu')
        for f in geo['features']:
            key=f['properties']['ADM0_A3'];color=cmap(norm(np.clip(values[key],-30,30))) if key in values else '#dedede'
            geom=f['geometry'];polys=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
            for poly in polys:ax.add_patch(Polygon(poly[0],facecolor=color,edgecolor='white',lw=.3))
        ax.set(xlim=(-180,180),ylim=(-60,85),xlabel='Longitud (grados)',ylabel='Latitud (grados)',title='9 · Cambio 2023–2024 de producción de vino (%)')
        ax.set_aspect('equal');fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),ax=ax,label='Variación (%)',shrink=.7)
        fig.text(.01,.005,'Natural Earth 1:110m · Proyección equirectangular (referencia, áreas distorsionadas) · Gris: fuera de tabla OIV',fontsize=8)
    elif number==10:
        for country,c in zip(['Italia','Francia','España'],['#7B1E3A','#087F8C','#91670C']):
            sub=o[o.pais==country];ax.plot(sub.anio,sub.produccion_mhl,label=country,color=c,marker='o')
        ax.set(xlabel='Año de producción',ylabel='Millones de hectolitros (mhl)',ylim=(0,60),xticks=range(2015,2025),title='10 · Producción anual: tres grandes productores');ax.tick_params(axis='x',rotation=45);ax.legend()
    return fig

if __name__=='__main__':
    for i in range(1,11):
        f=static_chart(i);f.savefig(ROOT/f'figuras/{i:02d}.png',bbox_inches='tight');plt.close(f)

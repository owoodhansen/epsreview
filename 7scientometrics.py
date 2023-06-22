
################ imports
import pandas as pd
from collections import Counter
import plotly.express as px
import base64
# from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',400)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

raw= pd.read_csv("data/3allcoded.csv")
raw.columns

#### Prep data: 
eps = raw[(raw['exclude'] == 0)].reset_index(drop=True)
len(raw), len(eps)


# prep: publication names
eps.pubname = eps.pubname.replace({'Sustainability (Switzerland)': 'Sustainability', 'Science of the Total Environment': 'Science of The Total Environment', 'Energy & Fuels': 'Energy and Fuels'})
eps['articletype'].value_counts()
eps['documenttype'].value_counts()


#################### Count journals, number of articles ##################
epsjour = eps[eps['documenttype'] == 'journal article']
len(eps), len(epsjour)
epsjour.pubname.str.lower().value_counts()
pd.Series(epsjour.pubname.value_counts()).to_clipboard()
len(epsjour.pubname.unique())


######################Scientometric figures ##########

# prep: time series

pubtimes = pd.DataFrame(eps.pubyear.value_counts()).reset_index()
pubtimes = pubtimes.rename(columns={'index': 'year', 'pubyear': 'hits'})
# pubtimes = pubtimes[pubtimes.year < 2023]
pubtimes['year'] = pd.to_datetime(pubtimes['year'], format='%Y')
pubtimes = pubtimes.sort_values('year')

######## prep data: methods
emps = eps[eps['articletype'] == "empirical"]
emps = emps[emps['counter'] != "only"]
len(emps)

emps[emps['agg method'].isna()]

meth = pd.Series([i.lower() for i in emps['agg method']])
meth.str.replace('model')
meth = meth.str.split(",").explode().tolist()
meth = [i.strip() for i in meth]
meth = pd.Series(Counter(meth)).sort_values(ascending=True).reset_index()
meth.columns = ['method', 'frequency']
meth['frequency'] = meth['frequency'].astype('int')

othermod = meth.loc[meth['frequency'] < 6,:].sum().copy()
diffother = sum(meth['frequency'] < 6)
meth = meth.loc[meth['frequency'] > 5, :].reset_index(drop=True)

meth.loc[-1] =  [f'Other methods ({diffother} different)', othermod['frequency']]
meth.index = meth.index + 1
meth = meth.sort_index()
len(meth)

meth['method'] = meth['method'].astype('str')
meth['method'] = meth['method'].str.capitalize()
meth
meth['method'] = meth['method'].replace({'Lca': 'LCA', 'Mfa': 'MFA', 'Iam': 'IAM', 'Synthesis of previous literature with analysis': 'Literature synthesis and analysis'})

########################  STAND ALONE FIGURES ########################################
###### Figure, pubyear, stand-alone 

fig1 = px.bar(pubtimes, x='year', y='hits' , 
             template='simple_white' , 
             labels={'hits': 'No. of publications', 'year': 'Publication year'}, 
             )
fig1.update_layout(bargap=0.01,title_y=0,font_size=11, width=500, height=300)
fig1.update_xaxes(tickfont=dict(size=10))
fig1.update_yaxes(tickfont=dict(size=10), dtick=10)
fig1.update_traces(marker_color='#008cf9')
fig1.update_layout(margin=dict(l=80, r=30, t=25, b=65))

fig1.show()
pio.write_image(fig1,"figures/timeseries.png", scale=2)

######### Figure, methods, stand-alone

fig2 = px.bar(meth, y='method', x='frequency', orientation="h", 
              labels={"frequency": "No. of studies"}, template='simple_white')                                          
fig2.update_layout(bargap=0.01, yaxis_title=None, font_size=11, width=500, height=300)
fig2.update_traces(marker_color='#008cf9')
fig2.update_xaxes(range=[0, 49.5],tickfont=dict(size=10), dtick=10)
fig2.update_yaxes(tickfont=dict(size=10))

image_filename = 'figures/brokenaxis1.png'
plotly_logo = base64.b64encode(open(image_filename, 'rb').read())

fig2.update_layout(images=[
        dict(
            source= 'data:image/png;base64,{}'.format(plotly_logo.decode()),
            xref="x", yref="paper",
            x=42, y=1.040,
            sizex=5, sizey=5,
            layer="above"),
        dict(
            source= 'data:image/png;base64,{}'.format(plotly_logo.decode()),
            xref="x", yref="paper",
            x=42, y=0.07,
            sizex=5, sizey=5,
            layer="above")
]
)

fig2.add_annotation(x=48, y="LCA",
            text=f"{meth['frequency'].max()}",
            showarrow=False, font=dict(color="white", size=10))

fig2.update_layout(    margin=dict(l=50, r=30, t=25, b=65))

fig2.show()
pio.write_image(fig2,"figures/meth.png", scale=2)

################## FIGURES AS SUBPLOTS ####################################


figsub = make_subplots(
    rows=1, cols=2, 
    print_grid=True, 
   # vertical_spacing = 1,
    horizontal_spacing = 0.25,
    # subplot_titles=("Method titles", "Publication title")
)

# subplot 1
figsub.add_trace(go.Bar(x=pubtimes['year'], y=pubtimes['hits'], marker_color='#008cf9'), row=1, col=1)

figsub.update_xaxes(title_text="Publication year", tickfont=dict(size=10), range=['2002-06-1', '2022-06-1'], row=1, col=1)
figsub.update_yaxes(title_text="No. of studies", side='left', tickfont=dict(size=10), dtick=10, row=1, col=1)

# subplot 2
figsub.add_trace(go.Bar(y=meth['method'], x=meth['frequency'], orientation="h", marker_color='#008cf9'), row=1, col=2)

figsub.update_xaxes(title_text="No. of studies", tickfont=dict(size=10), dtick=10, range=[0, 49.5], row=1, col=2)
figsub.update_yaxes(tickfont=dict(size=10), ticks="", row=1, col=2)

## annotations ("count LCA studies + subplot titles")

figsub['layout'].update(annotations=[
    dict(xref='x2', yref='y2', #specifies subplot one, see print_grid=True in make_subplots
        x=48, y="LCA", text=f"{meth['frequency'].max()}", showarrow=False, font=dict(color="white", size=10)
        ),
    dict(xref='paper', yref='paper', x=-0.05, y=-0.15, text="(a)", showarrow=False, font=dict(color="black", size=12)),
    dict(xref='paper', yref='paper', x=.58, y=-0.15, text="(b)", showarrow=False, font=dict(color="black", size=12)) 
    ])


## Add broken axis image
# Copy image from miro, within an obsidian canvas, to get transparent png 

image_filename = 'figures/brokenaxis1.png'
plotly_logo = base64.b64encode(open(image_filename, 'rb').read())

figsub.update_layout(images=[
        dict(
            source= 'data:image/png;base64,{}'.format(plotly_logo.decode()),
            xref="x2",
            yref="paper",
            x=42,
            y=1.035,
            sizex=5,
            sizey=5,
            layer="above"),
        dict(
            source= 'data:image/png;base64,{}'.format(plotly_logo.decode()),
            xref="x2",
            yref="paper",
            x=42,
            y=0.05,
            sizex=5,
            sizey=5,
            layer="above")
]
)

# full figure
figsub.update_layout(showlegend=False, template="simple_white", bargap=0.01, font_size=11)
#figsub.update_layout(margin=dict(l=25, r=25, b=25, t=25))
figsub.update_layout(width=1000, height=500)

figsub.show()


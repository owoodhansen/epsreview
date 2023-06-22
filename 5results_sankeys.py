## Oskar, EPS

### Script 5: Get "empirical" results and sankey diagrams ############################
# Pre-script: Manually screen and classify all relevant EPS articles. 
# I) Count mitigation options, count impacts
# I) Count results for all mitigation, and disaggregated CDR, SHW, Other
# II) Construct sankey diagrams with Jupyter interactive, remember to change ##OPTIONS### in script to build the different diagrams
# ##################################### 

import pandas as pd
from collections import Counter
import color_tol
from floweaver import *
from ipysankeywidget import SankeyWidget

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

#################

raw= pd.read_csv("data/3allcoded.csv")
raw.columns
eps_n_counter = raw[(raw['exclude'] == 0) & (raw['articletype'] == "empirical")].reset_index(drop=True)
eps = eps_n_counter[eps_n_counter['counter'] != "only"]
len(raw), len(eps), len(eps_n_counter)

eps['miti measure'].map(type).unique() # columns agg impact and miti measure are objects only containing strings

sankdat = eps[['miti measure', 'split measure', 'agg impact', 'split agg impact']].reset_index(drop=True)

sankdat = sankdat.replace("marine environment", "biodiversity and ecosystem functioning")
sankdat = sankdat.replace("biodiversity and ecosystem functioning, marine environment", "biodiversity and ecosystem functioning")
sankdat[sankdat['agg impact'].str.contains("marine environment")] # check

########### Count mitigation options occurences
cmslst = sankdat['miti measure'].str.split(';').explode().tolist()
cmslst = [i.strip().strip("(").strip(")") for i in cmslst]
mitioptions_list = pd.Series(Counter(cmslst)).sort_values(ascending=False)
mitioptions_list

########### Count env impact occurence
eilst = sankdat['agg impact'].str.split(',').explode()
eilst = eilst.str.split(';').explode().tolist()
eilst = [i.strip().strip("(").strip(")") for i in eilst]
pd.Series(Counter(eilst)).sort_values(ascending=False)

# ozone layer, ozone formation. Classified as AIR POLL and HUMAN TOX respectively.


### prep / collate small miti into "other" category
other = ['Biobased economy', 'Hydrogen carriers', 'Diet change', 'Agricultural management', 'Waste-to-energy', 'Reduced conversion of forests', 'Nuclear']             
sankoth = sankdat[sankdat['miti measure'].str.contains(('|').join(other), regex=True)]
sankdat['miti measure'] = sankdat['miti measure'].replace(other, "Other", regex=True)

############# Make "OTHER" sankey   ##################
sankoth = sankoth.drop(['split agg impact', 'split measure'], axis =1).copy()
sankoth

sankoth[sankoth['miti measure'].str.contains(";")] # check
# remove non-other, manually
sankoth.loc[65:66] = [['Biobased economy', 'eutrophication and biogeochemical flows'], ['Biobased economy', 'human toxicity']]
sankoth.loc[182] = ['Hydrogen carriers', 'eutrophication and biogeochemical flows, land use, mineral and metal depletion']

sankoth['agg impact'] = sankoth['agg impact'].str.split(",")
sankoth = sankoth.explode(['agg impact'])

sankoth['miti measure'] = sankoth['miti measure'].str.strip()
sankoth['agg impact'] = sankoth['agg impact'].str.strip()
sankoth['miti measure'].unique(), sankoth['agg impact'].unique()

sankoth = sankoth[['miti measure', 'agg impact']].groupby('miti measure').value_counts().reset_index()
sankoth.to_clipboard(index=False) 

############ EXPLODE NORMAL ###############
sankall = sankdat.drop(['split agg impact', 'split measure'], axis =1).copy()
sankall['miti measure'] = sankall['miti measure'].str.split(";") # Split mitigation
sankall['agg impact'] = sankall['agg impact'].str.split(";")  # Split impacts
sankall = sankall.explode(['miti measure', 'agg impact']) # multi explode

sankall['agg impact'] = sankall['agg impact'].str.split(",") # Second split on impacts, split on ";" 
sankall = sankall.explode('agg impact') # explode impacts

sankall['miti measure'] = sankall['miti measure'].str.strip()
sankall['agg impact'] = sankall['agg impact'].str.strip()
sankall['miti measure'].unique(), sankall['agg impact'].unique()

sankall = sankall[['miti measure', 'agg impact']].groupby('miti measure').value_counts().reset_index()

sankall.to_clipboard(index=False)

###### CDR EXPLODE ##########################
sankcdr = sankdat[sankdat['miti measure'].str.contains("CDR")].copy()
sankcdr = sankcdr.drop(['agg impact', 'miti measure'], axis =1).copy()

sankcdr[sankcdr['split measure'].str.contains(";")] # check
# one row with "bioenergy; CDR" fucks it up. manual edit
sankcdr.loc[74] = ['ARR', "acidification, eutrophication and biogeochemical flows, water use"] 

sankcdr['split measure'] = sankcdr['split measure'].str.split(";") 
sankcdr['split measure'].explode().str.strip().value_counts() # count number of CDR miti options
sankcdr['split agg impact'] = sankcdr['split agg impact'].str.split(";") 
sankcdr = sankcdr.explode(['split measure', 'split agg impact'])

sankcdr['split agg impact'] = sankcdr['split agg impact'].str.split(",") 
sankcdr = sankcdr.explode(['split agg impact'])

pd.Series(Counter(sankcdr['split agg impact'].str.strip())).sort_values()

sankcdr['split measure'] = sankcdr['split measure'].str.strip()
sankcdr['split agg impact'] = sankcdr['split agg impact'].str.strip()
sankcdr['split measure'].unique(), sankcdr['split agg impact'].unique()

sankcdr = sankcdr[['split measure', 'split agg impact']].groupby('split measure').value_counts().reset_index()
sankcdr = sankcdr.rename(columns={'split measure': 'miti measure', 'split agg impact': 'agg impact'})

sankcdr.to_clipboard(index=False)

###### SHW EXPLODE ####################################
sankshw = sankdat[sankdat['miti measure'].str.contains("SHW")].copy()
sankshw = sankshw.drop(['agg impact', 'miti measure'], axis =1).copy()

sankshw[sankshw['split measure'].str.contains(";")] # check
# manual edit out of bioenergy
sankshw.loc[137:138] = ['solar; wind', 'biodiversity and ecosystem functioning; biodiversity and ecosystem functioning' ]

sankshw['split measure'] = sankshw['split measure'].str.split(";") 
sankshw['split measure'].explode().str.strip().value_counts() # count number of SHW miti options
sankshw['split agg impact'] = sankshw['split agg impact'].str.split(";") 
sankshw = sankshw.explode(['split measure', 'split agg impact'])

sankshw['split agg impact'] = sankshw['split agg impact'].str.split(",") 
sankshw = sankshw.explode(['split agg impact'])

sankshw['split measure'] = sankshw['split measure'].str.strip()
sankshw['split agg impact'] = sankshw['split agg impact'].str.strip()
sankshw['split measure'].unique(), sankshw['split agg impact'].unique()

sankshw = sankshw[['split measure', 'split agg impact']].groupby('split measure').value_counts().reset_index()
sankshw = sankshw.rename(columns={'split measure': 'miti measure', 'split agg impact': 'agg impact'})

sankshw.to_clipboard(index=False)

##################
## Sankey NODE ORDERING
ALLmiti = ['Bioenergy', 'Low-carbon\n electricity systems', 'Solar, hydro &\n wind power', 'CDR', 'CCS & CCU', 'Electric vehicles', 'Carbon pricing', 
      'General mitigation', 'Other' ]
CDRmiti = ['ARR', 'BECCS', 'DACCS', 'Biochar', 'EW', 'Ocean F', 
       'SCS', 'Ocean AE']
SHWmiti = ['Wind', 'Solar', 'Hydro']
OTHmiti = ['Biomaterials', 'Hydrogen\n carriers', 'Diet change', 'Agricultural \nmanagement', 'Waste-to-energy', 'Reduced conversion \nof forests']

# PALETTE: dict mapping doesnt work. Colours are just applied in order
paletteALL = {
    'Bioenergy': '#00a76c',
    'Low-carbon\n electricity systems': '#b80058',
    'Solar, hydro\n & wind power': '#e45903',
    'CDR': '#008cf9',
    'CCS + CCU': '#ebac23',
    'Electric vehicles': '#d163e6',
    'Carbon pricing': '#674ea7', 
    'General mitigation': '#878500',
    'Other': '#00bbad',
    }
paletteCDR = {
    'ARR': '#00a76c',   # surfgreen
    'BECCS':  '#b80058', # lipstick
    'Biochar': '#008cf9', # bluesky 
    'DACCS': '#d163e6', # codeinepurple
    'Enhanced weathering': '#00bbad',  # turqoise    
    'Ocean fertilisation': '#ebac23', # yellow
    'Oceanic alkalinity enhancement': '#5954d6', # darkpurple 
    'SCS': '#b24502' #orange
}
paletteSHW = {'Solar': '#00a76c', 'Wind': '#b80058', 'Hydro': '#008cf9'}
paletteOTH = {'Biomaterials': '#00a76c', 
              'Hydrogen carriers': '#b80058' , 
              'Diet change': '#008cf9',
              'Agricultural management': '#ebac23' , 
              'Waste-to-energy': '#d163e6', 
              'Reduced conversion of forests': '#5954d6' }
# https://www.color-hex.com/
# colour blind alternative palette: color_tol.qualitative(8).html_colors
cblind = color_tol.qualitative(9).html_colors
####################################
############## OPTIONS #############

sankvc = sankoth  # lowercase
aaa = OTHmiti # CDRmiti / ALLmiti / SHWmiti / OTHmiti
palette = paletteOTH # paletteALL, paletteSHW, paletteOTH, paletteCDR / cblind
sankeydiagramname = "oth_flows_small"
# also change size, if required. below
# also change naming replacements (ctrl K then ctrl C, uncomment first K then U)

####################################
###################################
 
sankvc = sankvc.reset_index(drop=True)
sankvc['agg impact'] = sankvc['agg impact'].str.capitalize()

# sankvc = sankvc.replace({'Low carbon electricity': 'Low-carbon\n electricity systems', 
#                          'CCS + CCU': 'CCS & CCU', 
#                          'SHW': 'Solar, hydro &\n wind power', 
#                          'Eutrophication and biogeochemical flows':  'Eutrophication & \nbiogeochemical flows',  # 'Eutro. & biogeochem.', #
#                          'Biodiversity and ecosystem functioning':  'Biodiversity & \necosystem functioning', # 'Biodiv. & ES func.'
#                          'Oceanic alkalinity enhancement': 'Ocean AE',
#                          'Water use': 'Freshwater use',
#                          'Enhanced weathering': 'EW',
#                          'Ocean fertilisation': 'Ocean F', 
#                          'Land use':  'Land use & \ndegradation ', # 'Land Use & Deg.',
#                          'Unspecified environmental effects of mining':  'Environmental effects \nof mining', #  'Env. effects of mining',
#                          'Mineral and metal depletion': 'Mineral & metal \ndepletion', # 'M&M depletion', 
#                          'Agricultural management': 'Agricultural \nmanagement',
#                          'Reduced conversion of forests': 'Reduced conversion \nof forests', 
#                          'hydro': 'Hydro', 'wind': 'Wind', 'solar': 'Solar',   
#                          'Biobased economy': 'Biomaterials' , 
#                          'Hydrogen carriers': 'Hydrogen \ncarriers'                   
#                          })

sankvc = sankvc.replace({'Low carbon electricity': 'Low-carbon\n electricity systems', 
                         'CCS + CCU': 'CCS & CCU', 
                         'SHW': 'Solar, hydro &\n wind power', 
                         'Eutrophication and biogeochemical flows':  'Eutro. & biogeochem.', 
                         'Biodiversity and ecosystem functioning':  'Biodiv. & ES func.',
                         'Oceanic alkalinity enhancement': 'Ocean AE',
                         'Water use': 'Freshwater use',
                         'Enhanced weathering': 'EW',
                         'Ocean fertilisation': 'Ocean F', 
                         'Land use':  'Land Use & Deg.',
                         'Unspecified environmental effects of mining':   'Env. effects of mining',
                         'Mineral and metal depletion': 'M & M depletion', 
                         'Agricultural management': 'Agricultural \nmanagement',
                         'Reduced conversion of forests': 'Reduced conversion \nof forests', 
                         'hydro': 'Hydro', 'wind': 'Wind', 'solar': 'Solar',   
                         'Biobased economy': 'Biomaterials' , 
                         'Hydrogen carriers': 'Hydrogen\n carriers',
                         'Waste-to-energy': 'Waste-to-energy'                  
                         })

sankvc = sankvc.rename(columns={'miti measure': 'source', 'agg impact': 'target', 0: 'value'})
sankvc['share_by_source'] = sankvc['value'] / sankvc.groupby('source')['value'].transform('sum')
sankvc['share_by_impact'] = sankvc['value'] / sankvc.groupby('target')['value'].transform('sum')

# remove relatively small impacts
# sankvc = sankvc[sankvc['share_by_source'] > 0.1]

dataset = Dataset(sankvc)
# sankvc['source'].unique().tolist() 

bbb = sankvc['target'].unique().tolist() # alphabetic order
# preferred order: ( by size)
#   ['water use',  'land use', 'biodiversity and ecosystem functioning', 'eutrophication and biogeochemical flows',
#   'human toxicity', 'air pollution', 'mineral and metal depletion', 'ecotoxicity', 'acidification',  
#   'unspecified environmental effects of mining', 'marine environment'
#   ]
         
nodes = {'measures': ProcessGroup(aaa), 'impacts': ProcessGroup(bbb) }
ordering = [['measures'], ['impacts']]
bundles = [Bundle('measures', 'impacts')]

sdd = SankeyDefinition(nodes, bundles, ordering, flow_partition = dataset.partition('source'))

nodes['measures'].partition = Partition.Simple('process', values=aaa)
nodes['impacts'].partition = Partition.Simple('process', bbb)

## dimming scale

class DimmingCategoricalScale(CategoricalScale):
    # Grey out threshold flows, 
    def __init__(self, attr, threshold_measure, threshold_value, **kwargs):
        """Acts like CategoricalScale unless threshold_measure is below threshold_value."""
        super().__init__(attr, **kwargs)
        self.threshold_measure = threshold_measure
        self.threshold_value = threshold_value

    def __call__(self, link, measures):
        value = measures[self.threshold_measure]
        if value < self.threshold_value:
            return '#eeeeee'
        return super().__call__(link, measures)
    
my_scale3 = DimmingCategoricalScale(
    'source', # should colour categories be based on source or target nodes
    threshold_measure='share_by_source',
    threshold_value=0.0,
    palette=palette # cblind
)    

### FIGURES ################### 
## If I want to remove threshold flows alltogether, use #sankvc = sankvc[sankvc['share_by_source'] > 0.1]
# run in jupyter interactive (plugin)
y = 1.6
size_optionsfull = dict(width=800*1.1, height=875*1.1, margins=dict(left=175, right=175, top=-50, bottom=-50))
size_optionstall = dict(width=725*1.1, height=875*1.1, margins=dict(left=175, right=175, top=-50, bottom=-50))
size_optionsCDR = dict(width=300*y, height=250*y, margins=dict(left=100, right=170, top=0, bottom=0))
size_optionsSHW = dict(width=300*y, height=220*y, margins=dict(left=100, right=170, top=0, bottom=0))
size_optionsOTH = dict(width=330*y, height=220*y, margins=dict(left=140, right=170, top=0, bottom=0))

w = weave(sdd, sankvc, measures={'value': 'sum', 'share_by_source': 'sum'}, 
          link_color=my_scale3, link_width='value').to_widget(**size_optionsOTH)
w


# and save. NB change filename: 
w.auto_save_png(f"sankey/{sankeydiagramname}.png")

# Numbers on flows? https://nbviewer.org/github/ricklupton/ipysankeywidget/blob/master/examples/More%20examples.ipynb#Link labels 
# w.scale = 1.2 Widens the thickness of flows
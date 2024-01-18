
################

import pandas as pd
import color_tol
from floweaver import *
from ipysankeywidget import SankeyWidget
from helperscripts.sankeyhelps import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

################# LOAD ##############

sheetnames = [ "miti options","env impacts", "all-compact", "all-full", 'other', 'cdr', 'shw' ]
shifts = pd.read_excel("results\shiftcounts.xlsx", sheet_name= sheetnames )

dataframes = [shifts[name] for name in sheetnames]
a,b,all,d,oth,cdr,shw = [i[:] for i in dataframes]


####################################
############## OPTIONS #############

sankvc =            oth
aaa =               othmiti     # cdrmiti / allmiti / shwmiti / othmiti
sankeydiagramname = "oth_flows"
size_options =      sizeoth     # sizefull, sizeall, sizecdr, sizeshw, sizeoth
palette =           palette_oth # palette_all, palette_shw, palette_oth, palette_cdr
node_description_length = short # long, short

####################################
###################################
 
sankvc = sankvc.reset_index(drop=True)
sankvc['agg impact'] = sankvc['agg impact'].str.capitalize()

sankvc = sankvc.replace(node_description_length)

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

### FIGURES ################### 
## If I want to remove threshold flows alltogether, use #sankvc = sankvc[sankvc['share_by_source'] > 0.1]
# run in jupyter interactive (plugin)
my_scale3 = DimmingCategoricalScale(
    'source', # should colour categories be based on source or target nodes
    threshold_measure='share_by_source',
    threshold_value=0.0,
    palette = palette
)    

### cblind palettes: # https://www.color-hex.com/ 

my_scale3cblind = DimmingCategoricalScale(
    'source', # should colour categories be based on source or target nodes
    threshold_measure='share_by_source',
    threshold_value=0.0,
    palette= color_tol.qualitative(len(sankvc.iloc[:,0].unique())).html_colors
)    

w1 = weave(sdd, sankvc, measures={'value': 'sum', 'share_by_source': 'sum'}, 
          link_color=my_scale3, link_width='value')

w2 = weave(sdd, sankvc, measures={'value': 'sum', 'share_by_source': 'sum'}, 
          link_color=my_scale3cblind, link_width='value')

# and save. NB change filename: 
w1.to_widget(**size_options).auto_save_png(f"sankey/{sankeydiagramname}.png")
w1.to_widget(**size_options).auto_save_svg(f"sankey/{sankeydiagramname}.svg")

w2.to_widget(**size_options).auto_save_png(f"sankey/{sankeydiagramname}_cblind.png")
w2.to_widget(**size_options).auto_save_svg(f"sankey/{sankeydiagramname}_cblind.svg")

# Numbers on flows? https://nbviewer.org/github/ricklupton/ipysankeywidget/blob/master/examples/More%20examples.ipynb#Link labels 
# w.scale = 1.2 Widens the thickness of flows
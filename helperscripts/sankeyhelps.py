
# PALETTES: dict mapping doesnt work. Colours are just applied in order
palette_all = {
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

palette_cdr = {
    'ARR': '#00a76c',   # surfgreen
    'BECCS':  '#b80058', # lipstick
    'Biochar': '#008cf9', # bluesky 
    'DACCS': '#d163e6', # codeinepurple
    'Enhanced weathering': '#00bbad',  # turqoise    
    'Ocean IF': '#ebac23', # yellow
    'Oceanic AE': '#5954d6', # darkpurple 
    'SCS': '#b24502' #orange
    }

palette_shw = {
    'Solar': '#00a76c',
    'Wind': '#b80058', 
    'Hydro': '#008cf9'
    }

palette_oth = {
    'Biomaterials': '#00a76c', 
    'Hydrogen carriers': '#b80058' , 
    'Diet change': '#008cf9',
    'Agricultural management': '#ebac23' , 
    'Waste-to-energy': '#d163e6', 
    'Reduced conversion of forests': '#5954d6' 
    }

## Sankey NODE ORDERING
allmiti = ['Bioenergy', 'Low-carbon\n electricity systems', 'Solar, hydro &\n wind power', 'CDR', 'CCS & CCU', 'Electric vehicles', 'Carbon pricing', 
      'General mitigation', 'Other' ]
cdrmiti = ['ARR', 'BECCS', 'DACCS', 'Biochar', 'EW', 'Ocean IF', 
       'SCS', 'Ocean AE']
shwmiti = ['Wind', 'Solar', 'Hydro']
othmiti = ['Biomaterials', 'Hydrogen\n carriers', 'Diet change', 'Agricultural \nmanagement', 'Waste-to-energy', 'Reduced conversion \nof forests']


#### node desciption  format

short = {'Low carbon electricity': 'Low-carbon\n electricity systems', 
                         'CCS + CCU': 'CCS & CCU', 
                         'SHW': 'Solar, hydro &\n wind power', 
                         'Eutrophication and biogeochemical flows':  'Eutro. & biogeochem.', 
                         'Biodiversity and ecosystem functioning':  'Biodiv. & ES func.',
                         'Oceanic alkalinity enhancement': 'Ocean AE',
                         'Water use': 'Freshwater use',
                         'Enhanced weathering': 'EW',
                         'Ocean iron fertilisation': 'Ocean IF', 
                         'Land use':  'Land Use & deg.',
                         'Unspecified environmental effects of mining':   'Env. effects of mining',
                         'Mineral and metal depletion': 'M & M depletion', 
                         'Agricultural management': 'Agricultural \nmanagement',
                         'Reduced conversion of forests': 'Reduced conversion \nof forests', 
                         'hydro': 'Hydro', 'wind': 'Wind', 'solar': 'Solar',   
                         'Biobased economy': 'Biomaterials' , 
                         'Hydrogen carriers': 'Hydrogen\n carriers',
                         'Waste-to-energy': 'Waste-to-energy'                  
                         }
         

long = {'Low carbon electricity': 'Low-carbon\n electricity systems', 
                         'CCS + CCU': 'CCS & CCU', 
                         'SHW': 'Solar, hydro &\n wind power', 
                         'Eutrophication and biogeochemical flows':  'Eutrophication & \nbiogeochemical flows', 
                         'Biodiversity and ecosystem functioning':  'Biodiversity & \necosystem functioning',
                         'Oceanic alkalinity enhancement': 'Ocean AE',
                         'Water use': 'Freshwater use',
                         'Enhanced weathering': 'EW',
                         'Ocean iron fertilisation': 'Ocean IF', 
                         'Land use':  'Land use & \ndegradation ', # 'Land Use & Deg.',
                         'Unspecified environmental effects of mining':  'Environmental effects \nof mining', #  'Env. effects of mining',
                         'Mineral and metal depletion': 'Mineral & metal \ndepletion', # 'M&M depletion', 
                         'Agricultural management': 'Agricultural \nmanagement',
                         'Reduced conversion of forests': 'Reduced conversion \nof forests', 
                         'hydro': 'Hydro', 'wind': 'Wind', 'solar': 'Solar',   
                         'Biobased economy': 'Biomaterials' , 
                         'Hydrogen carriers': 'Hydrogen \ncarriers'                   
                         } 


# sizes

sizefull = dict(width=800*1.1, height=875*1.1, margins=dict(left=175, right=175, top=-50, bottom=-50))
sizeall = dict(width=725*1.1, height=875*1.1, margins=dict(left=175, right=175, top=-50, bottom=-50))
sizecdr = dict(width=480, height=400, margins=dict(left=140, right=170, top=0, bottom=0))
sizeshw = dict(width=480, height=350, margins=dict(left=140, right=170, top=0, bottom=0))
sizeoth = dict(width=480, height=350, margins=dict(left=140, right=170, top=0, bottom=0))

from floweaver import *
from ipysankeywidget import SankeyWidget

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

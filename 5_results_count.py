
################


import pandas as pd
from collections import Counter

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',500)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

#################

raw= pd.read_csv("data/manualdata/5scopus_zot_IPCC_v2.csv")
raw.articletype.value_counts()

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
eilst = pd.Series(Counter(eilst)).sort_values(ascending=False)
eilst

# ozone layer, ozone formation. KEEP INSIDE AIR POLL and HUMAN TOX, because not sure its noted/coted for all studies 

###########################################################
#################### COUNTING SHIFTS ######################
###########################################################½

############  ALL SHIFTS, FULL ###############
sankallfull = sankdat.drop(['split agg impact', 'split measure'], axis =1).copy()
sankallfull['miti measure'] = sankallfull['miti measure'].str.split(";") # Split mitigation
sankallfull['agg impact'] = sankallfull['agg impact'].str.split(";")  # Split impacts
sankallfull = sankallfull.explode(['miti measure', 'agg impact']) # multi explode

sankallfull['agg impact'] = sankallfull['agg impact'].str.split(",") # Second split on impacts, split on ";" 
sankallfull = sankallfull.explode('agg impact') # explode impacts

sankallfull['miti measure'] = sankallfull['miti measure'].str.strip()
sankallfull['agg impact'] = sankallfull['agg impact'].str.strip()
sankallfull['miti measure'].unique(), sankallfull['agg impact'].unique()

sankallfull = sankallfull[['miti measure', 'agg impact']].groupby('miti measure').value_counts().reset_index()

############  ALL SHIFTS, OTHER COLLATED ###############

# prep / collate small miti into "other" category
other = ['Biobased economy', 'Hydrogen carriers', 'Diet change', 'Agricultural management', 'Waste-to-energy', 'Reduced conversion of forests', 'Nuclear']             
sankoth = sankdat[sankdat['miti measure'].str.contains(('|').join(other), regex=True)].copy()
sankdat['miti measure'] = sankdat['miti measure'].replace(other, "Other", regex=True)

# explode
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

############# OTHER SHIFTS  ##################
sankoth = sankoth.drop(['split agg impact', 'split measure'], axis =1).copy()
sankoth = sankoth.reset_index(drop=True)

sankoth[sankoth['miti measure'].str.contains(";")] # check
# remove non-other, manually
sankoth.loc[6] = ['Biobased economy', 'human toxicity']
sankoth.loc[8] = ['Hydrogen carriers', 'eutrophication and biogeochemical flows, land use, mineral and metal depletion']
sankoth.loc[11] = ['Biobased economy', 'eutrophication and biogeochemical flows']

sankoth['agg impact'] = sankoth['agg impact'].str.split(",")
sankoth = sankoth.explode(['agg impact'])

sankoth['miti measure'] = sankoth['miti measure'].str.strip()
sankoth['agg impact'] = sankoth['agg impact'].str.strip()
sankoth['miti measure'].unique(), sankoth['agg impact'].unique()

sankoth = sankoth[['miti measure', 'agg impact']].groupby('miti measure').value_counts().reset_index()

###### CDR SHIFTS ##########################
sankcdr = sankdat[sankdat['miti measure'].str.contains("CDR")].copy()
sankcdr = sankcdr.drop(['agg impact', 'miti measure'], axis =1)
sankcdr = sankcdr.reset_index(drop=True)

sankcdr[sankcdr['split measure'].str.contains(";")] # check
# Rows with CDR and other mitigation measure, like "bioenergy; CDR" causes issue. manual edits:
sankcdr.loc[1] = ['ARR', "acidification, eutrophication and biogeochemical flows, water use"] 
sankcdr.loc[50] = ['DACCS', 'air pollution'] 
sankcdr.loc[51] = ['BECCS', 'water use, human toxicity'] 
sankcdr.loc[52] = ['BECCS', 'land use'] 

sankcdr['split measure'] = sankcdr['split measure'].str.split(";") 
cdr_options = sankcdr['split measure'].explode().str.strip().value_counts().copy() # count number of CDR miti options
sankcdr['split agg impact'].explode().str.strip().value_counts() # count number of CDR miti options
sankcdr['split agg impact'] = sankcdr['split agg impact'].str.split(";") 
sankcdr = sankcdr.explode(['split measure', 'split agg impact'])

sankcdr['split agg impact'] = sankcdr['split agg impact'].str.split(",") 
sankcdr = sankcdr.explode(['split agg impact'])

cdr_impacts = pd.Series(Counter(sankcdr['split agg impact'].str.strip())).sort_values()

sankcdr['split measure'] = sankcdr['split measure'].str.strip()
sankcdr['split agg impact'] = sankcdr['split agg impact'].str.strip()
sankcdr['split measure'].unique(), sankcdr['split agg impact'].unique()

sankcdr = sankcdr[['split measure', 'split agg impact']].groupby('split measure').value_counts().reset_index()
sankcdr = sankcdr.rename(columns={'split measure': 'miti measure', 'split agg impact': 'agg impact'})

###### SHW SHIFTS ####################################
sankshw = sankdat[sankdat['miti measure'].str.contains("SHW")].copy()
sankshw = sankshw.drop(['agg impact', 'miti measure'], axis =1)
sankshw = sankshw.reset_index(drop=True)

sankshw[sankshw['split measure'].str.contains(";")] # check
# manual edit out of bioenergy
sankshw.loc[[26,28]] = ['solar; wind', 'biodiversity and ecosystem functioning; biodiversity and ecosystem functioning' ]
sankshw.loc[23] = ['hydro', 'biodiversity and ecosystem functioning, land use' ]
sankshw.loc[37] = ['hydro', 'water use' ]

sankshw['split measure'] = sankshw['split measure'].str.split(";") 
shw_options = sankshw['split measure'].explode().str.strip().value_counts().copy() # count number of SHW miti options
sankshw['split agg impact'] = sankshw['split agg impact'].str.split(";") 
sankshw = sankshw.explode(['split measure', 'split agg impact'])

sankshw['split agg impact'] = sankshw['split agg impact'].str.split(",") 
sankshw = sankshw.explode(['split agg impact'])

sankshw['split measure'] = sankshw['split measure'].str.strip()
sankshw['split agg impact'] = sankshw['split agg impact'].str.strip()
sankshw['split measure'].unique(), sankshw['split agg impact'].unique()

sankshw = sankshw[['split measure', 'split agg impact']].groupby('split measure').value_counts().reset_index()
sankshw = sankshw.rename(columns={'split measure': 'miti measure', 'split agg impact': 'agg impact'})
sankshw

##### 

# sankoth.to_clipboard(index=False) 

# cdr_impacts
cdr_options
shw_options


with pd.ExcelWriter("results\shiftcounts.xlsx") as writer:
   
    mitioptions_list.to_excel(writer, sheet_name="miti options")
    eilst.to_excel(writer, sheet_name="env impacts")
    cdr_options.to_excel(writer, sheet_name="cdr options")
    sankall.to_excel(writer, sheet_name="all-compact", index=False)
    sankallfull.to_excel(writer, sheet_name="all-full", index=False)
    sankoth.to_excel(writer, sheet_name="other", index=False)
    sankcdr.to_excel(writer, sheet_name="cdr", index=False)
    sankshw.to_excel(writer, sheet_name="shw", index=False)


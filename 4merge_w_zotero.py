import pandas as pd
import numpy as np

## Idea structure

# Combine zot + scopus
# Remove duplicates, choose scopus over zot

################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

####  Prep scopus data
newscopus = pd.read_csv("data/1cleaned_oct.csv").loc[:,'eid':] # There are 19 doi = NaN
len(newscopus)
sum(newscopus.doi.isna())

coded = pd.read_csv("data/old/7allcodedv7.csv") # NB: There are 18 doi = "no doi" 
len(coded)

# Find deltas in new7updated scopus call (by subtracting coded dois from 7allcoded.csv)
newscopus_alreadycoded = (newscopus.doi.isin(coded.doi))
sum(newscopus_alreadycoded)
deltascopus = newscopus[~newscopus.doi.isin(coded.doi)] # 19 NaN dois in are kept in delta
len(deltascopus)

# now check delta docs against screening master (previously manually scanned docs) 
mst = pd.read_csv("data/backup_scanned_ids/4eids_manuallyscanned.csv", encoding='utf-8-sig').loc[:, 'eid':]
### NB: New master "4_master_scanned_october.csv"

mst.EPS.value_counts() # EPS are integers

sum(deltascopus.eid.isin(mst.eid)) # 2281 eids are already in mst


delta_mst = deltascopus.merge(mst, how="left", on="eid") # Now left merge master onto scopus_deltas
len(delta_mst)
 # this means that all the mst.EPS = 0 can be removed from scopus delta, the 1's have to be looked over, along with the non-matches

delta_mst.EPS.value_counts()
delta_mst[delta_mst.EPS == 1] # One is already in allcodedm, the other eid = 2-s2.0-85043476305 must be added

nevercoded = (delta_mst.EPS.isna()) # Now the only real delta docs to check manually are those which are EPS = na
sum(nevercoded)
deltafin = delta_mst[nevercoded]
len(deltafin)

# NB dont remove doi duplicates, that just removes NaN dois
deltafin[deltafin.doi.duplicated()]

####  test if doi-nans are removed by master_eid
deltana = deltascopus[deltascopus.doi.isna()]
deltana
sum(delta_mst.doi.isna())
delta_mst[delta_mst.doi.isna()] 
# Some doi-nans are removed by mst, as they have been screened previously (correct) 

deltafin.to_csv("data/manualdata/scopusdelta_oct.csv", encoding='utf-8-sig', index=False)
# scanned manually and add to 7allcodedv7


################## Do everything zotero after
#### prep zotero


zot = pd.read_csv("data/manualdata/EPSfromzotero2023nov.csv")
len(zot)
zot = zot.drop_duplicates('itemKey')
zot['itemType'].unique()
zot =  zot[['DOI','ISBN', 'ISSN', 'abstractNote', 'automatic_tag', 'collection', 'creators',  'publicationTitle', 'tag', 'title', 'year', 'itemType']]
zot = zot.rename(str.lower, axis='columns')
zot = zot.rename(columns={'abstractnote': 'description', 'automatic_tag': 'authkeywords','collection': 'zotfolder','creators':  'author_names','publicationtitle': 'pubname', 'tag': 'zot-tag', 'year': 'pubyear'})
zot['description'] = zot['description'].str.replace("\n", " ")


sum(zot.doi.value_counts() > 1) # ingen doi duplicates
sum(zot.isbn.value_counts() > 1) # ingen isbn dups
zot.doi = zot.doi.fillna("no doi")
zot[zot.doi == "no doi"]['title'].sort_values() # no title duplicates
len(zot)
sum(zot.doi.duplicated())

### Combine prepped zotero and prepped scopus

scopus = pd.read_csv("data/manualdata/scopusdelta_tocode.csv")
len(scopus)


combined = pd.concat([scopus, zot], ignore_index=True)
len(combined)

# drop duplicates, prefer scopus. 
# Checked titles manually, no duplicates
sum(combined.doi.isna())
combined.doi.value_counts()
len(combined)

nodoimask = combined.doi == 'no doi'
combined = pd.concat([combined.drop_duplicates(['doi'], keep='first'), combined[nodoimask]]) # keep first, given that scopus are listed before zots

combined['description'] = combined['description'].str.replace("\n", " ")
combined['description'] = combined['description'].str.replace("abstract", "", case=False).str.replace("All Rights Reserved", "", case=False)

len(combined)
combined = combined.drop(columns=['Unnamed: 0', 'aggregationType', 'source_id', 'pii', 'author_count', 'title_ed', 'description_ed', 'authkeywords_ed'])

combined = combined.drop_duplicates("title", keep="first")

combined.to_csv("data/manualdata/5scopus_zot_ipcc.csv", encoding='utf-8-sig', index=False)

#### 

# Save scanned DOIs from combined dataset 

np.setdiff1d(coded['doi'],zotjrs['doi'])

[item for item in zotjrs['doi'] if item not in coded['doi']]
main_list

coded['doi']

# How many ZOTS are actually added now? 
sum(combined['itemtype'].isna()==False)
sum(combined['doi'].isna())
combined.columns
 
coded = pd.read_csv("data/7allcodedv7.csv")
len(coded)
sum(coded['doi'].isna())
coded.columns
coded = coded.drop(columns=['subtype', 'title', 'affilname', 'author_count',
       'author_names', 'citedby_count', 'zotfolder', 'zot-tag', 'issn',
       'pubyear', 'pubname', 'description', 'authkeywords'])

oldnew = combined.merge(coded, how="left", on="doi")
len(oldnew)
oldnew.columns

oldnew = oldnew[['link', 'url', 'doi', 'eid',  'issn', 'isbn', 'subtype', 'affilname', 'citedby_count', 'date', 'journal_count', 'subjabbr', 'subjarea', 'subjcode', 'EPS', 'zotfolder', 'zot-tag', 'itemtype', 'author_names', 'pubyear', 'pubname', 'authkeywords', 'description', 'title', 'ALLTEXT',
       'TAK word search', 'exclude', 'Review', 'Exclusion reason', 'Counter?',
       'Study type', 'Review summary', 'miti measure', 'miti measure lvl 2',
       'Sector', 'miti measure lvl 3', 'miti measure lvl 4', 'Note',
       'agg method', ' method', 'agg impact', 'agg impact CDR specific',
       'Environmental impact', 'EI subtype', 'How / channel', 'Unnamed: 37']]

oldnew.to_csv("data/manualdata/june2scan.csv", encoding='utf-8-sig', index=False)



zot = pd.read_csv("data/manualdata/EPSfromzotero.csv")
len(zot)
zot = zot.drop_duplicates('itemKey')
zot['itemType'].unique()
### zot = zot[zot['itemType'] == 'journalArticle']
zot =  zot[['DOI','ISBN', 'ISSN', 'abstractNote', 'automatic_tag', 'collection', 'creators',  'publicationTitle', 'tag', 'title', 'year', 'itemType']]
zot = zot.rename(str.lower, axis='columns')
zot = zot.rename(columns={'abstractnote': 'description', 'automatic_tag': 'authkeywords','collection': 'zotfolder','creators':  'author_names','publicationtitle': 'pubname', 'tag': 'zot-tag', 'year': 'pubyear'})
zot['description'] = zot['description'].str.replace("\n", " ")


sum(zot.doi.value_counts() > 1) # ingen doi duplicates
sum(zots.isbn.value_counts() > 1) # ingen isbn dups
zot.doi = zot.doi.fillna("no doi")
zot[zot.doi == "no doi"]['title'].sort_values() # no title duplicates
len(zot)


# Merge previously screened zotero EPS onto new zots
zot_doimaster = pd.read_csv("data/backup_scanned_ids/4_zotdois_manscanned.csv").loc[:, 'doi':]
zots = zot.merge(zot_doimaster, how="left", on="doi")
len(zot_doimaster), len(zot), len(zots)
prescre_zot = zots[zots['EPS'] != 0]
len(zots) 
# now we have newest zotero, ready to be scanned. Pre-scanned non-EPS are removed already. 

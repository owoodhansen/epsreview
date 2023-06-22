## Oskar, EPS

### Script 4: Merge manually searched results and filtered SCOPUS results ############################
# Pre-step: Export from personally Zotero database 
# I) Import Zotero results, prepare for merge 
# II) Import filtered scopus, prepare for merge
# III) Merge and check for duplicates
# Post-script: Manually screen and classify all relevant EPS articles. 
# ##################################### 

import pandas as pd

################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

##################
#### prep zotero

zot = pd.read_csv("data/manualdata/EPSfromzotero.csv")
len(zot)
zot = zot.drop_duplicates('itemKey')
zot['itemType'].unique()
### zot = zot[zot['itemType'] == 'journalArticle']
zot =  zot[['DOI','ISBN', 'ISSN', 'abstractNote', 'automatic_tag', 'collection', 'creators',  'publicationTitle', 'tag', 'title', 'year', 'itemType']]
zot = zot.rename(str.lower, axis='columns')
zot = zot.rename(columns={'abstractnote': 'description', 'automatic_tag': 'authkeywords','collection': 'zotfolder','creators':  'author_names','publicationtitle': 'pubname', 'tag': 'zot-tag', 'year': 'pubyear'})
zot['description'] = zot['description'].str.replace("\n", " ")

zot.doi.value_counts() # ingen doi duplicates
zots.isbn.value_counts()
zot.doi = zot.doi.fillna("no doi")
zot[zot.doi == "no doi"]['title'].sort_values() # no title duplicates
len(zot)

# remove duplicates in zotero (if they exist in multiple collections)
namask = zot.isbn.isna()
zot = pd.concat([zot.drop_duplicates(['isbn']), zot[namask]])
len(zot)

# now we have newest zotero, ready to be manually screened. 

####  Prep scopus data
scopus = pd.read_csv("data/2cleaned.csv").loc[:,'eid':]
len(scopus)
scopus.tail()

scopus.doi = scopus.doi.fillna("no doi")

### Combine prepped zotero and prepped scopis

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

# How many ZOTS are actually added now? 
sum(combined['itemtype'].isna()==False)
sum(combined['doi'].isna())
combined.columns

combined.to_csv("data/2litt_for_manualscreening.csv", encoding='utf-8-sig', index=False)
# Post-script: Manually screen and classify all relevant EPS articles. 


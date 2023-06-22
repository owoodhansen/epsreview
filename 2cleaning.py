# Oskar, EPS


### Script 2: Filtering of SCOPUS results ############################
# I) Filter by subject areas
# II) Filters at journal level
# III) Filters at article level
# ##################################### 

import pandas as pd
from scopusquery import badarticlewords, badjournaltitles, badjournaltitlewords

################

res = pd.read_csv("data/1scopus_initfilters.csv")
res = res.loc[:,'eid':]
len(res)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_colwidth', 150)

res.columns
################# preparation

[row for row in res.description if len(row)<5] # checks for empty abstracts
len([row for row in res.authkeywords if len(row)<5]) # check for empty keywords

sum(res["pubname"].isna())
res = res[~res["pubname"].isna()]

# make ABS-KW-TIT searchable, lowercase
res['description_ed'] = [i.lower().strip().replace("  ", " ") for i in res.description]
res['authkeywords_ed'] = [i.lower().strip().replace("  ", " ") for i in res.authkeywords]

# duplicate test
dups_doi = ((res['doi'].duplicated(keep=False)) & (res['doi'].isna() == False) )
res = res[~dups_doi]
dups_eid = ((res['eid'].duplicated(keep=False)) & (res['eid'].isna() == False) )
sum(dups_eid), sum(dups_doi)


# prep 
res[res['subjabbr'].isna()]
res = res[res['eid'] != "2-s2.0-0032010175"] # remove one article without data. Also irrelevant, about migration

############## FILTERING ###########################

len(res)
################## Clean on subject level

#### Clean all articles that dont have high-level subjects
neccsubj = ['ECON', 'ENVI', 'EART', 'ENER']

# filter
mask_neccsubj = res['subjabbr'].str.contains('|'.join(neccsubj))
sum(~mask_neccsubj)
res = res[mask_neccsubj]

################# Remove adaptation papers, if not also a mitigation

# remove if contains adaptation, but not mitigation
adap = res[['description_ed', 'authkeywords_ed', 'title_ed']].applymap(lambda x: 'adaptation' in x).any(axis=1)
miti = res[['description_ed', 'authkeywords_ed', 'title_ed']].applymap(lambda x: 'mitigation' in x).any(axis=1)
sum(adap), sum(miti), sum((adap & ~miti))
res = res[ ~(adap & ~miti)]

############################
len(res)

# Take deljournallist and find which excluded journals are actually in dataset

journalmask = [i in badjournaltitles for i in res.pubname]
len(badjournaltitles)
deljrs_relevant = pd.Series(res[journalmask]['pubname'].unique())
len(deljrs_relevant)
deljrs_relevant.to_clipboard(excel=True, sep=None, index=False, header=None)
########

# Journals: remove irrelevant titles, by manual list of titles or by exclusion terms in title
delj1 = res['pubname'].isin(badjournaltitles) # irrelevant jrnl titles, by jrnal title.  decided by checking art_titles of jrnls with more than 5 articles
delj3 = res['pubname'].str.contains('|'.join(badjournaltitlewords), case=False, na=False) # remove jrnls containing keywords which indicate irrelevant niches
res[delj3]['pubname'].sample(10) # to check
print(sum(delj1), sum(delj3), '. accounting for overlaps between del1 and del2:', sum(delj1)) 
sum(delj1 | delj3), sum(delj1 | delj3) - sum(delj1 )
res = res[~(delj1 |delj3)]
len(res)

# Journal: remove  journals with only one article
singlejournal =(res['journal_count'] <= 1) # removes journals with only one article that fitted orig query
res[singlejournal].to_csv("data/testsinglejournal.csv", encoding='utf-8-sig', index = False)
sum(singlejournal) 
res = res[~(singlejournal)]

# Articles: Remove articles with low cites
lowcite_newpap = ((res.citedby_count <= 3) & (res.date < "2018-01-01") ) # removes articles that are older than 5 years and 1 or less citations
lowcite_oldpap = ((res.citedby_count <= 5) & (res.date < "2013-01-01") ) # removes articles that are older than 10 years and 5 or less citations
print(sum(lowcite_newpap), sum(lowcite_oldpap),  ". articles deleted, acc for overlaps: ", sum(lowcite_newpap | lowcite_oldpap))
res = res[~(lowcite_newpap | lowcite_oldpap)]
len(res)


################## Clean bad KW in article titles

# remove badwords in TAK
mask_badwordsTAK = res[['description_ed', 'authkeywords_ed', 'title_ed']].applymap(lambda x: any(y in x for y in badarticlewords)).any(axis=1)
sum(mask_badwordsTAK)

# tests
res[mask_badwordsTAK]['title'].sample(10) # to check

res = res[~mask_badwordsTAK]
len(res)
res.shape
res.ndim
################# SAVE

len(res)
res.to_csv("data/2cleaned.csv",  encoding='utf-8-sig', index = False)
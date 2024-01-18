# Oskar, EPS

### Script 2: Filtering of SCOPUS results ############################
# 0) Filter by time, doctype
# I) Filter by subject areas
# II) Filters at journal level
# III) Filters at article level
# ##################################### 

import pandas as pd
from helperscripts.scopusquery import badwords, EPSdeljournals, deljournals2, badjrnlnames
import string

################

df_subj = pd.read_csv("data/0subjarea_data_nofilter.csv")
len(df_subj)

df = pd.read_csv("data/0raw_nofilter_v1.csv")
len(df)

################## Initial cleaning

len(df)

oldarts = df[df["pubyear"] <= 1985]
len(oldarts) # if little number, don't remove

df['date'] = pd.to_datetime(df['date'])
toonew = df['date'] > pd.datetime(2023,4,30)
sum(toonew)
df = df[~toonew]

len(df)

no_jrnl = df.aggregationType != 'Journal' # ONLY ARTICLES, not books / conf papers
sum(no_jrnl)
df = df[~no_jrnl]
len(df)


df.aggregationType.value_counts() 
df.subtype.value_counts() 

doctypes = ~df.subtype.isin(["ar", "re"])
sum(doctypes)
df = df[~doctypes]

# remove doi duplicates
dups = ((df['doi'].duplicated(keep=False)) & (df['doi'].isna() == False) & (df['subtype'].isin(['ar', 're'])))
sum(dups)
df = df[~dups]

# check art_title duplicates after lowercase and removing punc 
punctoremove = string.punctuation.replace("-", "")
df['title_ed'] = [i.translate(str.maketrans('', '', punctoremove)) for i in df.title] # Also removes hyphen, and not only dash
df['title_ed'] = [i.lower().strip().replace("  ", " ") for i in df.title_ed]
dups_edtitle = df['title_ed'].duplicated(keep=False)
sum(dups_edtitle) 
df = df[~dups_edtitle]

# removes reprints and three manually found doi duplicates 
reprints = df[df['title_ed'].str.contains('reprint')]['doi']
reprintdois = [str(x) for x in reprints]
manremovals = df['doi'].isin(['10.1016/j.envsci.2013.08.001', '10.3763/cpol.2002.0216', '10.1080/15567030903330645']+reprintdois)
sum(manremovals)
df = df[~manremovals]
len(df)

res = df

len(res)
######## MERGE

res = res.loc[:,'eid': ]
df_subj.columns
fulldat = pd.merge(res, df_subj, how='left', on='eid')

len(fulldat)
# some cleaning after merge
fulldat = fulldat.drop_duplicates(subset=['title_ed'])
fulldat['publicationName'] = [html.unescape(stryng) for stryng in fulldat['publicationName']]

# Tjek at pubtitler er ens i API'er
x = fulldat[~(fulldat.publicationName == fulldat.pubname)]
x[["publicationName", 'pubname']]


# rename some that differ
fulldat.loc[fulldat["publicationName"] == "Environmental Change and Security Project report", 'pubname'] = "Environmental Change and Security Project report"
fulldat['pubname'] = fulldat['pubname'].replace({"Journal of environmental management": "Journal of Environmental Management",
                            "International journal of environmental research and public health": "International Journal of Environmental Research and Public Health",
                            }) 
# leave gaia as is
fulldat.pubname.fillna(fulldat.publicationName, inplace=True)
fulldat = fulldat.drop(['publicationName'], axis=1)

fulldat.to_csv("data/0fulldat_v1.csv",  encoding='utf-8-sig', index=False)

len(fulldat)

res = pd.read_csv("data/0fulldat_v1.csv")
res = res.loc[:,'eid':]
len(res)

len(res.pubname.unique())

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
len(res.pubname.unique())

#### Clean all articles that dont have high-level subjects
neccsubj2 = ['ECON', 'ENVI', 'EART', 'ENER', 'AGRI', 'MULT']

# filter
mask_neccsubj2 = res['subjabbr'].str.contains('|'.join(neccsubj2))
sum(~mask_neccsubj2)
res = res[mask_neccsubj2]

len(res)
len(res.pubname.unique())
# ### Filter on specific ASJC subject area codes
# subjtermlist = [1105, 1207, 1400, 1401, 1405, 1900, 1901, 1902, 1904, 1906, 1908, 1910, 1911, 1912, 2000, 2001, 2002, 2003, 2100, 2102, 2104, 2105, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2308, 2309, 2310, 2311, 2312, 3300, 3301, 3305, 3308, 3312, 3313, 3320, 3321, 3303]

# asjc = pd.read_csv('data/manualdata/ASJC.csv') # to get names corresponding to codes for suppl material
# asjc[asjc.code.isin(subjtermlist)].asjccat.to_clipboard()

# #xx = res.subjarea.apply(ast.literal_eval)
# #xx = [element for sublist in xx for element in sublist]

# # filter on the asjc codes
# res.subjcode = [row.strip('][').split(', ') for row in res.subjcode]
# res.subjcode = [[int(i) for i in row] for row in res.subjcode]
# masksubjcodes = [any(artsubjs in subjtermlist for artsubjs in article) for article in res.subjcode]
# len(masksubjcodes) - sum(masksubjcodes)

# #res = res[masksubjcodes]
# #len(res)

################# Remove adaptation papers, if not also a mitigation

# remove if contains adaptation, but not mitigation
adap = res[['description_ed', 'authkeywords_ed', 'title_ed']].applymap(lambda x: 'adaptation' in x).any(axis=1)
miti = res[['description_ed', 'authkeywords_ed', 'title_ed']].applymap(lambda x: 'mitigation' in x).any(axis=1)
sum(adap), sum(miti), sum((adap & ~miti))
res = res[ ~(adap & ~miti)]

############################
len(res)

# test
exremo_jnames = ["Agronomy", "European Journal of Forest Research", "Geoderma", "Hydrobiologia", "Marine Pollution Bulletin", "Mires and Peat", "Oecologia", "Water Resources Management"]
tyt = res['pubname'].isin(exremo_jnames)
sum(tyt)
res[tyt].to_clipboard()

# Take deljournallist and find which journals are deleted in dataset
journalmask = [i in EPSdeljournals+deljournals2 for i in res.pubname]
len(EPSdeljournals+deljournals2)
deljrs_relevant = pd.Series(res[journalmask]['pubname'].unique())
len(deljrs_relevant)
deljrs_relevant.to_clipboard(excel=True, sep=None, index=False, header=None)

######## len(res.pubname.unique())
len(res.pubname.unique())

# Remove articles in irrelevant journals
delj1 = res['pubname'].isin(EPSdeljournals) # irrelevant jrnl titles, by jrnal title
delj2 = res['pubname'].isin(deljournals2) #  decided by checking art_titles of jrnls with more than 5 articles
print(sum(delj1), sum(delj2), sum(delj3), '. accounting for overlaps between del1 and del2:', sum(delj1 |delj2)) 

res = res[~(delj1 |delj2)]
len(res)
len(res.pubname.unique())
delj3 = res['pubname'].str.contains('|'.join(badjrnlnames), case=False, na=False) # remove jrnls containing keywords which indicate irrelevant niches
# res[delj3]['pubname'].sample(10) # to check

res = res[~(delj3)]
len(res)
len(res.pubname.unique())

sum(delj1 |delj2 | delj3), sum(delj1 |delj2 | delj3) - sum(delj1 |delj2)

# Further cleaning
singlejournal =(res['journal_count'] <= 1) # removes journals with only one article that fitted orig query
res[singlejournal].to_csv("data/testsinglejournal.csv", encoding='utf-8-sig', index = False)
sum(singlejournal) 
res = res[~(singlejournal)]

len(res.pubname.unique())

lowcite_newpap = ((res.citedby_count <= 3) & (res.date < "2018-01-01") ) # removes articles that are older than 5 years (and 11m) and 1 or less citations
lowcite_oldpap = ((res.citedby_count <= 5) & (res.date < "2013-01-01") ) # removes articles that are older than 10 years (and 11m) and 5 or less citations
print(sum(lowcite_newpap), sum(lowcite_oldpap),  ". articles deleted, acc for overlaps: ", sum(lowcite_newpap | lowcite_oldpap))
res = res[~(lowcite_newpap | lowcite_oldpap)]
len(res)
len(res.pubname.unique())

################## Clean bad KW in article titles

# remove badwords in TAK
mask_badwordsTAK = res[['description_ed', 'authkeywords_ed', 'title_ed']].applymap(lambda x: any(y in x for y in badwords)).any(axis=1)
sum(mask_badwordsTAK)

# remove badwords in title only
mask_badwordstitle = res['title_ed'].apply(lambda x: any(y in x for y in badwords))
sum(mask_badwordstitle)
res[mask_badwordstitle]['title'].sample(10) # to check

# tests
res[mask_badwordsTAK]['title'].sample(10) # to check
#res.iloc[443,]
#res.iloc[5189,]['description']

res = res[~mask_badwordsTAK]
len(res)
res.shape
res.ndim
################# SAVE

len(res)
len(res.pubname.unique())
res.to_csv("data/1cleaned_oct.csv",  encoding='utf-8-sig', index = False)
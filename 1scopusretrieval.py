## Oskar, EPS

### Script 1: SCOPUS SEARCH  ############################
# I) Send search query to scopus for literature
# II) Get subject areas for each document (another Scopus API)
# III) Performs initial filtering
##################################### 

import pandas as pd
from pybliometrics.scopus import ScopusSearch
from scopusquery import EPSquery
import string
import html

## SCOPUS FIELD: SUBJAREA(SOCI)

#################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_colwidth', 150)

#import locale
#locale.getpreferredencoding()

################ GET results

s = ScopusSearch(EPSquery, download=True, subscriber=True, refresh=True, verbose=True) # set download=True for fast, but result size only
s.get_results_size()
# must be on icta network/vpn to DL more than 5K results. 
# Also requires SCOPUS API Key

raw = pd.DataFrame(pd.DataFrame(s.results))
raw.head()

raw.columns

####### clean important columns

strcols = ['title', 'authkeywords', 'description']
pattern = '|'.join(['<inf>', '</inf>','<sup>', '</sup>'])

for colname in strcols: 
    # removes html tags and weird ampersands
    raw[colname] = [i if isinstance(i, str) else "0" for i in raw[colname]]
    raw[colname] = [html.unescape(stryng) for stryng in raw[colname]] # removes ampersands: "&amp;" 
    raw[colname] = raw[colname].str.replace(pattern, "", regex=True)
    raw[colname] = [stryng.strip() for stryng in raw[colname]]# removes trails
    raw[colname] = [stryng.strip("'") for stryng in raw[colname]]# removes quoted titles
    raw[colname] = [stryng.strip('"') for stryng in raw[colname]]# removes quoted titles

### proper date column and a articles-pr-journal-count
raw['date'] = pd.to_datetime(raw.coverDate)
raw['pubyear'] = raw['date'].dt.year
raw['journal_count']= raw.publicationName.map(raw.publicationName.value_counts())
wantedfields = ['eid', 'doi', 'pii', 'title', 'subtype', 'affilname','author_count', 'author_names','publicationName', 'issn', 'source_id', 'aggregationType', 'description', 'authkeywords', 'citedby_count', 'date', 'pubyear', 'journal_count']

df = raw[wantedfields]
len(df)

# save
df.to_csv("data/0rawscopus.csv", encoding='utf-8-sig') # "-sig" adds BOM bc. Excel
df = pd.read_csv("data/0rawscopus.csv")
len(df)

############# APIs for subject areas

# https://service.elsevier.com/app/answers/detail/a_id/15181/supporthub/scopus/
# https://service.elsevier.com/app/answers/detail/a_id/14882/supporthub/scopus/related/1/ What are Scopus Field Codes? 


from pybliometrics.scopus import AbstractRetrieval # searches for subject for given article
#print(pybliometrics.__version__) # dev version has sessions function. 3.3.0 does not
# SerialSearch cannot be used on titles, because it isnt exact search. issn doesn't give full results. 
# SerialTitle is only on Issn/e-issn
from time import sleep

rel_results_eid = df.eid.unique()
len(rel_results_eid)

unable_eids = []
eid_subjects = []

for i, eid in enumerate(rel_results_eid):
    try:
        st = AbstractRetrieval(f'{eid}', view='FULL', id_type='eid')
        xtz = st.subject_areas
        subjarea = [i.area for i in xtz]
        subjabbr = [i.abbreviation for i in xtz]
        subjcode = [i.code for i in xtz]
        eid_subjects.append([eid, st.publicationName, subjabbr, subjarea, subjcode])
        if (i+1)%900 == 0:
            sleep(61)
    except:
        unable_eids.append(eid)

len(unable_eids)

retry_unable_eids = []
for i, un_eid in enumerate(unable_eids):
    try:
        st = AbstractRetrieval(f'{un_eid}', view='FULL', id_type='eid')
        xtz = st.subject_areas
        subjarea = [i.area for i in xtz]
        subjabbr = [i.abbreviation for i in xtz]
        subjcode = [i.code for i in xtz]
        retry_unable_eids.append([eid, st.publicationName, subjabbr, subjarea, subjcode])
    except Exception as e:
        print("did not")
        print(un_eid, e)    

len(eid_subjects)
len(retry_unable_eids)

all_subject_data = eid_subjects + retry_unable_eids 

#lost one. EID could not be found: "2-s2.0-0032010175"

df_subj = pd.DataFrame(all_subject_data, columns=['eid', 'pubname', 'subjabbr', 'subjarea','subjcode'])

df_subj.to_csv("data/0scopus_subjarea_data.csv", encoding='utf-8-sig') # "-sig" adds BOM bc. Excel
df_subj = pd.read_csv("data/0scopus_subjarea_data.csv")
len(df)


############################################################

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

doctypes = ~df.subtype.isin(["ar", "re"]) # only reviews and articles
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

fulldat.to_csv("data/1scopus_initfilters.csv",  encoding='utf-8-sig', index=False)

len(fulldat)

############## 
 
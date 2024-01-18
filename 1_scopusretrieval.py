## Oskar, EPS, scopuscall

### Script 1: SCOPUS SEARCH  ############################
# I) Send search query to scopus for literature
# II) Get subject areas for each document (another Scopus API)
##################################### 

import pandas as pd
import pybliometrics.scopus as scopus 
from scopusquery import EPSq
import html
import requests

#################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_colwidth', 150)

#import locale
#locale.getpreferredencoding()

################ GET results

from pybliometrics.scopus.utils import config
print(config['Proxy']['ftp'])  # Show keys


with requests.Session() as s: 
    s = scopus.ScopusSearch(EPSq, download=True, subscriber=True, refresh=True, verbose=True) # set download=True for fast, but result size only
    
s.get_results_size()
# must be on icta network/vpn to DL more than 5K results. 

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
len(df)
df.to_csv("data/0raw_nofilter_v1.csv", encoding='utf-8-sig') # "-sig" adds BOM bc. Excel
df = pd.read_csv("data/0raw_nofilter_v1.csv")


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
len(df)
df_subj.to_csv("data/0subjarea_data_nofilter.csv", encoding='utf-8-sig') # "-sig" adds BOM bc. Excel




############################################################


# 
import pandas as pd
from collections import Counter

# import numpy as np

################
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_colwidth', 150)

import locale
locale.getpreferredencoding()

#################

xx = pd.read_csv("data/3allcoded.csv")
xx.columns
len(xx)

################## Count occurence of alt terms

# prep
xx['authkeywords'] = xx['authkeywords'].str.replace("|", ".").fillna("")
terms = xx[(xx['exclude'] == 0)]
len(terms)

terms['articletype'].value_counts()
empis, reviews, concs = [*dict([*terms.groupby('articletype')]).values()]
len(empis), len(reviews), len(concs)

for testset_i in [empis, concs, reviews, terms]:

    testset = testset_i

    TAK = testset['title'] + " " + '[SEP]' + " " + testset['authkeywords'] + " " + '[SEP]' + " " + testset['description'] 
    TAK = TAK.astype("str")
    TAK = [i.lower() for i in TAK]
    TAK = pd.Series(TAK).str.replace("-", " ").to_list()

    altlist = ["tradeoff", "trade off", "problem shift", "burden shift", "cascad", "interact", "interaction effect", "interdepend", "coupled", "coupli", "linkage", 
    "co benefit", "cobenefit", "disbenefit", "dis benefit", "co cost", "displace", "displacement", "co impact", "spill over", "spillover", "byproduct", "by product", 
    "ancillary", "adverse side effect", "side effect", "adverse effect", "unintended", "unanticipated", "feedback"]

    print("length", len(TAK)) 

    kwcounts = []
    for kw in altlist:
        count = sum(kw in s for s in TAK)
        kwcounts.append(count)
        
    kwcount = pd.DataFrame(zip(altlist, kwcounts))
    print(kwcount.sort_values(0)) # [kwcount[1]>0]

    # Check for double doublecounts: 		
    #	tradeoff, byproduct, cobenefit, couple, spillover	
            
    kwtestpairs = [['by product', 'byproduct'], ['tradeoff', 'trade off'], ['co benefit', 'cobenefit'],['spill over', 'spillover'], ['coupled', 'coupli'], ['adverse side effect', 'side effect']]

    def count_substrings(strings, substrings):
        count = 0
        for string in strings:
            for substring in substrings:
                if substring in string:
                    count += 1
                    break
        return count

    for pair in kwtestpairs:
        print(pair[0], count_substrings(TAK, pair))

############# count all words

# Almost no results for unintended impacts/effects. 
# No results for unanticipated.

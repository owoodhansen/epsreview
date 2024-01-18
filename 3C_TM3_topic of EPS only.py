
import pandas as pd
from bertopic import BERTopic 
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
import pickle


########

scopus = pd.read_csv("data/5combined.csv")

scopus['authkeywords'] = scopus['authkeywords'].str.replace("|", ".").fillna("")

TAK = scopus['title'] + '[SEP]' + scopus['authkeywords'].fillna("") + '[SEP]' + scopus['description'] 
docs = TAK.astype("str")
len(docs)

   
# Check avg length of docs
lenwords = [len(doc.split()) for doc in docs]
sum(lenwords)/len(lenwords)
print(len([i for i in lenwords if i >200]), "docs are >200", ", 1482 >256, 817 >300, 102 >400")

############# DISCUSSION #########
# "Max Sequence Length:". All_MiniLM-L12 is max 256 word pieces, default 128. allenai-specter is 512 
# Should I change sentence transformer after changing max sequence length

############## EMDEDDING MODELS #### https://www.sbert.net/docs/pretrained_models.html
# Tried all-MiniLM-L12-v2, paraphrase-MiniLM-L12-v2, allenai-specter, all-mpnet-base-v2, scivocab
# default L6 doesnt work well 

### Scivocab via FLAIR attempts 
# tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased') # from scivocab github, but doesnt say how to use tokenizer?
# scivocabmodel = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
# embed_model = scivocabmodel # WORKS!!!

# See new tip for pipeline-method on https://huggingface.co/allenai/scibert_scivocab_uncased/discussions/2#634ef7a88d0f051a450650a1
####################################

embeddingmodel = 'all-MiniLM-L12-v2' # 'all-MiniLM-L12-v2' / 'all-mpnet-base-v2' / 'allenai-specter' / 'paraphrase-MiniLM-L12-v2'
sentence_model = SentenceTransformer(embeddingmodel)
sentence_model.max_seq_length = 512

embeddings = sentence_model.encode(docs, show_progress_bar=True)

#Store sentences & embeddings on disc
with open(f'data/bertopic/embeds/430EPS_{embeddingmodel}.pkl', "wb") as fOut:
    pickle.dump({'sentences': docs, 'embeddings': embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)
   


############# DISCUSSION #########
# is k-means better than hdbscan? Swapping out HDBSCAN for k-Means will reduce in a significantly less accurate model. There are quite a few benefits to HDBSCAN over k-Means including outlier detection, hierarchical nature, density efficiency, etc.

# reduce topic size: 

#################

# 'all-MiniLM-L12-v2' / 'all-mpnet-base-v2' / 'allenai-specter' / 'paraphrase-MiniLM-L12-v2'
embedmodel = 'all-MiniLM-L12-v2'

#Load sentences & embeddings from disc
with open(f'data/bertopic/embeds/430EPS_{embedmodel}.pkl', "rb") as fIn:
    stored_data = pickle.load(fIn)
    stored_sentences = stored_data['sentences']
    stored_embeddings = stored_data['embeddings']
    
###### HYPERPARAMETERS
# Pre-compute embeddings: Nice, to iterate fast over different versions of the model, if trying to optimize it to a specific use case

### Non-edited TAK is better than edited. (still cleaned for ampersands and linebreaks)
### Leaf vs EOM [Go with LEAF]
# By readthedocs: If you are more interested in having small homogeneous clusters then you may find Excess of Mass has a tendency to pick one or two large clusters and then a number of small extra clusters. In this situation you may be tempted to recluster just the data in the single large cluster. Instead, a better option is to select 'leaf' as a cluster selection method. This will select leaf nodes from the tree, producing many small homogeneous clusters. 
# comparison 10,10, div=0.2/0.1. EOM gives fewer topics, smaller noise, larger clusters 
### Diversity [Go with 0.2]
# Same noise. 0.3 and 0.0 makes clusters top-heavy, 0.0 makes cat 0 largerst, b
### Top n words [Go with 10]: Less clusters, but more coherent. # default: 10. "Use 10-20",
### Min_cluster_size [Go with 10]: Gives a few more, but clearer clusters. #BERTopic min_topic_size == HDBSCAN min_cluster_size
### min_samples [Go with 10] 
### N neighbours [Go with 10]: 15 is def
##################################

vector_model = CountVectorizer(ngram_range=(1, 2), stop_words= "english")
umap_model = UMAP(n_neighbors=10, min_dist=0.00, random_state=42)
hdbscan_model = HDBSCAN(min_cluster_size=5, cluster_selection_method='eom', gen_min_span_tree=True, prediction_data = False) 

topic_model = BERTopic(vectorizer_model=vector_model,
                       #embedding_model=sentence_model, 
                       hdbscan_model= hdbscan_model,  
                       umap_model= umap_model,
                       diversity = 0.2, 
                       top_n_words=10, 
                       language="english", nr_topics="auto", verbose=True, calculate_probabilities=False
                       ) 

topics, probs = topic_model.fit_transform(stored_sentences, stored_embeddings)

len(topic_model.get_topic_info())
topic_model.get_topic_freq()

# Save
topic_model.save(f"data/bertopic/topicmodels/430EPS_takunedit_{embedmodel}")


########################### load saved model
topic_model = BERTopic.load(f"data/bertopic/topicmodels/q4_takunedit_{embedmodel}")

### Merge or reduce no of topics
topic_model.reduce_topics(stored_sentences, nr_topics=20)
# topic_model.merge_topics(docs, [10,12])

### ngrams to 3 
# topic_model.update_topics(docs, vectorizer_model=CountVectorizer(ngram_range=(1, 3), stop_words="english"))


###########################

topicswordprobs = pd.DataFrame(topic_model.get_topics())
topicswordprobs.columns = range(topicswordprobs.shape[1])
topicswords = topicswordprobs.applymap(lambda x: x[0])

topicsno = pd.DataFrame(topic_model.get_topic_info()['Topic'])

topicswords = pd.concat([topicsno.T,topicswords], axis=0).reset_index(drop=True)
topicswords

topic_model.get_topic_info()['Topic']
topicfreq = pd.DataFrame(topic_model.get_topic_freq().T)

topicdata = topicfreq.append(topicswords)
topicdata.T.to_clipboard()

#############################################

# visualise barchart + intertopic distance
figbar = topic_model.visualize_barchart(top_n_topics=60, n_words=10, height=300, width=300)
figdistance = topic_model.visualize_topics(top_n_topics=60, height=1000, width=1000)
figbar.show()
figdistance.show()

# hierarchy
hierarchical_topics = topic_model.hierarchical_topics(docs)
fighiera = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics, width=600)
fighiera.show()

tree = topic_model.get_topic_tree(hierarchical_topics)
topic_model.visualize_term_rank().show()
topic_model.visualize_term_rank(log_scale=True).show()

# visualise map of articles (takes a while)
figdocmap = topic_model.visualize_documents(stored_sentences, embeddings=stored_embeddings, hide_document_hover=True, height=1200, width=1600)
figdocmap.show()

# Save html figures:pathtoviz = "data/bertopic/viz/"
pathtoviz = "data/bertopic/viz/EPS430/"
figbar.write_html(pathtoviz + "fig_barchart.html")
figdistance.write_html(pathtoviz + "fig_distance.html")
fighiera.write_html(pathtoviz + "fig_hierachy.html")
figdocmap.write_html(pathtoviz + "fig_docmap.html")




################## add topic numbers and topic_words to docs

# Concatenate topic keywords
topicwordscombined = topicswords.T.iloc[:,1:].apply(lambda row: ','.join(row.values.astype(str)), axis=1)
topicwordlists = pd.concat([topicswords.T.iloc[:,0],topicwordscombined],axis=1)
topicwordlists.columns = ['topicnr', 'topicwords']

# Get topic number for each article 
topics = pd.DataFrame(topic_model._map_predictions(topic_model.hdbscan_model.labels_), columns=['topicnr'])
topics = pd.merge(topics, topicwordlists, how="left", on='topicnr')
topics

# Finally merge topicdata onto articles
scopus = scopus.rename(columns={'topicnr': 'oldtopicnr', 'topicwords': 'oldtopicwords'})
article_topics = pd.concat([scopus, topics], axis=1)

article_topics.columns

##### 
article_topics.to_csv("data/5combined_wtopics.csv",  encoding='utf-8-sig')

comb1 = combined[['doi', 'subtype', 'zot-tag', 'citedby_count', 'topicnr', 'topicwords', 'pubyear', 'author_names', 'pubname', 'title', 'authkeywords', 'description', 'CC?', 'Mitigation?', 'Other ED?', 'GHG shift', 'zotfolder']]
comb1.to_csv("data/manualdata/5combined_tolabel.csv", encoding='utf-8-sig', index=False)

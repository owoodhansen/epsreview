###

import pandas as pd
from sentence_transformers import SentenceTransformer
# from transformers import AutoTokenizer, AutoModel # The Hugging face way
import pickle

scopus = pd.read_csv("data/1cleaned_may.csv").iloc[:,2:] # /#("data/0fulldat.csv")
len(scopus)
scopus['authkeywords'] = scopus['authkeywords'].str.replace("|", ".").fillna("")
TAK = scopus['title'] + '[SEP]' + scopus['authkeywords'] + '[SEP]' + scopus['description'] 
docs = TAK
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
with open(f'data/bertopic/embeds/{embeddingmodel}_cleaned2023.pkl', "wb") as fOut:
    pickle.dump({'sentences': docs, 'embeddings': embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from omegaconf import OmegaConf
import pandas as pd
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN

class Topic_modeling_LDA():
  def __init__(self, data) -> None:
    self.data = data
    self.nlp = spacy.load('en_core_web_lg')
    self.stopwords = list(STOP_WORDS)
    self.stopwords = [word for word in self.stopwords if word != 'only']
    self.punctuations = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
  # Tokenize the sentence using spacy
  def spacy_tokenizer(self, sentence):
    sentence = str(sentence)
    sentence = sentence.lower()
    sentence = sentence.replace('chinese-','chinese')
    sentence = sentence.replace(u'\xa0', ' ')
    mytokens = self.nlp(sentence)
    mytokens = [word.lemma_.lower() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]
    mytokens = [ word for word in mytokens if word not in self.stopwords and word not in self.punctuations ]
    mytokens = " ".join([i for i in mytokens])
    return mytokens

def get_topic_lda(self, num_topics = 10):
  self.data = self.preprocess(self.data)
  vectorizer = CountVectorizer(min_df=5, max_df=0.9, stop_words='english', lowercase=True, token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}')
  data_vectorized = vectorizer.fit_transform(self.data)
  lda = LatentDirichletAllocation(n_components=num_topics, max_iter=10, learning_method='online',verbose=False)
  data_lda = lda.fit_transform(data_vectorized)
  print(f"LDA Model for CBC news:")
  self.selected_topics(lda, vectorizer, num_topics)

# Functions for printing keywords for each topic
def selected_topics(self, model, vectorizer, top_n):
    for idx, topic in enumerate(model.components_):
        print("Topic %d:" % (idx))
        print([(vectorizer.get_feature_names_out()[i], topic[i])
                        for i in topic.argsort()[:-top_n - 1:-1]])
def preprocess(self):
   self.data['processed'] = self.data['text'].apply(self.spacy_tokenizer)
   return data

class Topic_modeling_BERT():
  def __init__(self, omegafile) -> None:
      self.config = omegafile
  def topic_modeling_processing(self):
    data = pd.read_csv(self.config.screen.output.screen_path)
    data['processed'] = data['text'].apply(self.text_preprocess)
    articles = list(data['processed'])
    # Get embeddings for all the articles
    embedding_model = SentenceTransformer('thenlper/gte-small')
    embeddings = embedding_model.encode(articles, show_progress_bar=True)
    
    # We reduce the input embeddings from 384 dimenions to 5 dimenions
    n_components = self.config.topic_modeling_BERT.umap.n_comp
    metric = self.config.topic_modeling_BERT.umap.metric
    umap_model = UMAP(
    n_components=n_components, min_dist=0.0, metric=metric, random_state=42)
    reduced_embeddings = umap_model.fit_transform(embeddings)
    
    # We fit the model and extract the clusters
    min_cluster_size = self.config.topic_modeling_BERT.hdscan.min_cluster_size
    metric = self.config.topic_modeling_BERT.hdscan.metric
    cluster_selection_method = self.config.topic_modeling_BERT.hdscan.cluster_selection_method
    hdbscan_model = HDBSCAN(
        min_cluster_size=min_cluster_size, metric=metric, cluster_selection_method=cluster_selection_method 
    ).fit(reduced_embeddings)

    # Train our model with our previously defined models
    topic_model = BERTopic(
    embedding_model=embedding_model,
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    verbose=True
    ).fit(articles, embeddings)

    return topic_model
  # Some standard preprocess of text data
  def text_preprocess(self, sentence):
    sentence = str(sentence)
    sentence = sentence.lower()
    sentence = sentence.replace('chinese-','chinese')
    sentence = sentence.replace(u'\xa0', ' ')
    
    return sentence
   
if __name__ == "__main__":
  config = OmegaConf.load('./params.yaml')
  data = pd.read_csv(config.screen.output.screen_path)
  #agent_LDA = Topic_modeling_LDA(data)
  #agent_LDA.get_topic_lda()
  agent_BERT = Topic_modeling_BERT(config)  
  topic_model = agent_BERT.topic_modeling_processing()
  topic_model.get_topic_info()
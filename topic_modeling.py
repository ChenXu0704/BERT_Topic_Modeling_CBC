import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from omegaconf import OmegaConf
import pandas as pd

class Topic_modeling():
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
if __name__ == "__main__":
  config = OmegaConf.load('./params.yaml')
  data = pd.read_csv(config.screen.output.screen_path)
  agent = Topic_modeling(data)
  agent.get_topic_lda()

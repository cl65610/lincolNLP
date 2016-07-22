import pandas as pd
import numpy as np
from spacy.en import English
parser = English()
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import string
import re
from sklearn.cross_validation import train_test_split

#h/t to Nic Schrading for this custom TransformerMixin

# A custom stoplist
STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "ca"] + list(ENGLISH_STOP_WORDS))
# List of symbols we don't care about
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve"]

# Define a custom transformer to clean text using spaCy
class CleanTextTransformer(TransformerMixin):
    """
    Convert text to cleaned text
    """

    def transform(self, X, **transform_params):
        return [cleanText(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}

# A custom function to clean the text before sending it into the vectorizer
def clean_text(text):
    # get rid of newlines
    text = text.strip().replace("\n", " ").replace("\r", " ")

    # replace twitter @mentions
    mentionFinder = re.compile(r"@[a-z0-9_]{1,15}", re.IGNORECASE)
    text = mentionFinder.sub("@MENTION", text)

    # replace HTML symbols
    text = text.replace("&amp;", "and").replace("&gt;", ">").replace("&lt;", "<")

    # lowercase
    text = text.lower()

    return text

# A custom function to tokenize the text using spaCy
# and convert to lemmas
def tokenizeText(sample):

    # get the tokens using spaCy
    tokens = parser(sample)

    # lemmatize
    lemmas = []
    # for tok in tokens:
    #     lemmas.append(tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_)
    # tokens = lemmas
    #
    # # stoplist the tokens
    # tokens = [tok for tok in tokens if tok not in STOPLIST]
    #
    # # stoplist symbols
    # tokens = [tok for tok in tokens if tok not in SYMBOLS]
    good_pos = ['VERB', 'ADJ', 'ADV']
    # Remove entities
    tokens = [tok.lemma_.lower() for tok in tokens if tok.pos_ in good_pos]
    for tok in tokens:
        lemmas.append(tok)

    # remove large strings of whitespace
    while '' in tokens:
        tokens.remove('')
    while " " in tokens:
        tokens.remove(" ")
    while "\n" in tokens:
        tokens.remove("\n")
    while "\n\n" in tokens:
        tokens.remove("\n\n")
    while "``" in tokens:
        tokens.remove("``")

    return lemmas


df = pd.read_csv('/Users/codylaminack/Documents/Practice/lincoln/data/parsed_lincoln.csv')
df['clean_text'] = df['text'].apply(clean_text)
df.head()

vectorizer = TfidfVectorizer(ngram_range=(1,1), tokenizer=tokenizeText, stop_words=STOPLIST,
                            lowercase=True, max_df = 0.80, min_df=0.05)
X = vectorizer.fit_transform(df.text)
vectorizer.get_feature_names()

vect_df = pd.DataFrame(X.toarray(), columns=[vectorizer.get_feature_names()])
vect_df.shape
vect_df.head()

lda_range= range(1,20)
lda_eval = []

for n in lda_range:
    lda = LatentDirichletAllocation(n_topics=n, max_iter=5,
                                    learning_method='online', learning_offset=50.,
                                    random_state=0)
    lda.fit(vect_df)
    score = lda.score(vect_df)
    perplexity = lda.perplexity(vect_df)
    print n,score,perplexity
    lda_eval.append({'topics':n,'score':score,'perplexity':perplexity})

for item in lda_eval:
    print item

lda = LatentDirichletAllocation(n_topics=5, n_jobs=-1)


topics = lda.fit_transform(vect_df)
lda.perplexity(vect_df)
lda.score(vect_df)
topics[2545]
df.ix[2545].text

topic_df = pd.DataFrame(topics, columns = [1,2,3,4,5])
topic_df.head()

topics = df.join(topic_df)
topics[topics.title.str.contains('Gettysburg')]
topics['max_lda'] = topics[[1,2,3,4,5]].idxmax(axis=1)
topics.head()
topics.dtypes

import seaborn as sns
%matplotlib inline
sns.distplot(topics.max_lda)

topics.max_lda.value_counts()

topics[topics.max_lda == 5].sort_values(5, ascending=False)

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    print()

print_top_words(lda, vectorizer.get_feature_names(), 10)

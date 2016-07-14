import pandas as pd
from spacy.en import English

df = pd.read_csv('all_lincoln.csv')

df.drop('index', axis=1, inplace=True)

# Pull out the year that a text was written
df['year'] = df.text.str.extract(r'(18[0-9]{2})')


# Design some piece of regex that will pull out the
df['month'] = df.text.str.extract(r'(January|Jan|JANUARY|JAN|February|Feb|FEBRUARY|FEB|March|MARCH|Mar|MAR|April|APRIL|Apr|APR|May|MAY|June|JUNE|Jun|JUN|July|JULY|Jul|JUL|August|AUGUST|Aug|AUG|September|SEPTEMBER|Sep|SEP|October|OCTOBER|Oct|OCT|November|NOVEMBER|Nov|NOV|December|DECEMBER|Dec|DEC)')
df.head()

df.month.value_counts()

df.isnull().sum()

df[df.year.isnull() == True]

nlp = spacy.load('en')
parser = English()
example = u"There's a dog up there."
parsed = parser(unicode(df.text[1]))
nlp(unicode(df.text[1]))
parsed
for i in parsed:
    print i.orth_, i.pos_, i.lemma_
    print i.orth_,


for i in parsed:
    print i.orth_, i.ent_type_, i.pos_

for i in parsed.sents:
    print i 
    for word in i:
        if word.pos_ == 'ADV':
            print word, word.pos_

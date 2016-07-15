import pandas as pd
from spacy.en import English
import spacy

df = pd.read_csv('all_lincoln.csv')

df.drop('index', axis=1, inplace=True)

# Pull out the year that a text was written
df['year'] = df.text.str.extract(r'(18[0-9]{2})')


# Design some piece of regex that will pull out the
df['month'] = df.text.str.extract(r'(January|Jan|JANUARY|JAN|February|Feb|FEBRUARY|FEB|March|MARCH|Mar|MAR|April|APRIL|Apr|APR|May|MAY|June|JUNE|Jun|JUN|July|JULY|Jul|JUL|August|AUGUST|Aug|AUG|September|SEPTEMBER|Sep|SEP|October|OCTOBER|Oct|OCT|November|NOVEMBER|Nov|NOV|December|DECEMBER|Dec|DEC)')



# Load the relevant parser
nlp = spacy.load('en')
count = 0
parsed = []

for i in parsed[0:100]:
    print i
    for token in i:
        if token.ent_type_ == 'DATE':
            print token.orth_, token.ent_type_

test_df = df.iloc[0:20]
test_df.iloc[2]['parsed']

# This format works well for keeping the individual text objects toghether after parsing. Each one
# is stored as a list.
# Write a for loop that will iterate through all 6700 texts, parse them, and append the results of that parsing to a list.
parsed = []
count=0
for i in range(0, len(df.index)):
    parsed.append([nlp(df.iloc[i]['text'].decode('utf-8'))])
    count+=1
    if count %10 == 0:
        print count

parse_df = pd.DataFrame(parsed, columns = ['parsed'])
for token in parse_df.iloc[1].parsed:
    if token.pos_ != 'PUNCT':
        print token.orth_, token.pos_,'\n', token.lemma_

for text in parse_df.iloc[0:100].parsed:
    print '***'
    for token in text:
        if token.ent_type_ == 'DATE':
            print token
test = df.join(parse_df)
test.head()
test.iloc[35].parsed
# Playing around in Spacy
nlp(unicode(df.iloc[4].text))
print df.iloc[4].text

parser = English()
example = u"There's a dog up there."
parsed = parser(unicode(df.text[1]))

parsed

for i in parsed:
    print i.orth_, i.pos_, i.lemma_
    print i.orth_,


for i in parsed[1]:
    print i.orth_, i.ent_type_, i.pos_

for i in parsed.sents:
    print i
    for word in i:
        if word.pos_ == 'ADV':
            print word, word.pos_


for i in parsed[0:100]:
    print i
    for token in i:
        if token.ent_type_ == 'DATE':
            print token.orth_, token.ent_type_

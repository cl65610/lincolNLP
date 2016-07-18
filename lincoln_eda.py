import pandas as pd
from spacy.en import English
import spacy

df = pd.read_csv('all_lincoln.csv')

df.drop('index', axis=1, inplace=True)

# Pull out the year that a text was written
df['year'] = df.text.str.extract(r'(18[0-9]{2})')


# Design some piece of regex that will pull out the
df['month'] = df.text.str.extract(r'(January|Jan|JANUARY|JAN|February|Feb|FEBRUARY|FEB|March|MARCH|Mar|MAR|April|APRIL|Apr|APR|May|MAY|June|JUNE|Jun|JUN|July|JULY|Jul|JUL|August|AUGUST|Aug|AUG|September|SEPTEMBER|Sep|SEP|October|OCTOBER|Oct|OCT|November|NOVEMBER|Nov|NOV|December|DECEMBER|Dec|DEC)')

# Regex that tries to pull the ull date out of the text
df['full_date'] = df.text.str.extract(r'([aA-zZ]+\b[\W]+\d+[\W+|\s]+18[\d]{2})')

# Fill in some of the values that were null with the first date of the month
df.full_date.fillna(df.month+' 1, '+df.year, inplace=True)

#Pull out the brackets, and other odd characters from full date
df.full_date = df.full_date.str.replace('[', '')
df.full_date = df.full_date.str.replace(']', '')
df.full_date = df.full_date.str.replace('?', '')
df.full_date = df.full_date.str.replace('Jany', 'January')
df.full_date = df.full_date.str.replace('Feby', 'February')
df.full_date = df.full_date.str.replace('Novr', 'November')
df.full_date = df.full_date.str.replace('Decr', 'December')
df.full_date = df.full_date.str.replace('Octr', 'October')
df.full_date = df.full_date.str.replace('Augt', 'August')
df.full_date = df.full_date.str.replace(':', '.')
df.full_date = df.full_date.str.replace('---', '.')
df.full_date = df.full_date.str.replace('.', ',')

# This succesfully converts most of the dates to datetime, but I think that we can clean them up a little bit before hand by stripping out unnecessary punctuation, mapping abbreviations to full months, etc.
df['date'] = pd.to_datetime(df[df.full_date.isnull()==False].full_date, errors = 'coerce')

df.dtypes

df[df.date.isnull()==True].shape

# Drop the row values that have neither month nor year dates. Those can't be imputed. In all, we lost around 40 rows with that.
df.dropna(subset=['year'], inplace=True)
df.dropna(subset=['month'], inplace=True)
df.isnull().sum()




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
    print '***', len(text)
    for token in text:
        if token.pos_ == 'VERB':
            print token, token.lemma_
test = df.join(parse_df)
test.head()
test.iloc[35].parsed
# Playing around in Spacy
nlp(unicode(df.iloc[4].text))
print df.iloc[4].text

parser = English()
example = u"There's a dog up there."
parsed = parser(unicode(df.text[1]))



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

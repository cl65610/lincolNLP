import pandas as pd
from spacy.en import English
import spacy
from spacy.attrs import ORTH
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.dates as dates
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
%matplotlib inline

df = pd.read_csv('/Users/codylaminack/Documents/Practice/lincoln/data/all_lincoln.csv')

df.drop('index', axis=1, inplace=True)

# Pull out the year that a text was written
df['year'] = df.text.str.extract(r'(18[0-9]{2})')


# Design some piece of regex that will pull out the
df['month'] = df.text.str.extract(r'(January|Jan|JANUARY|JAN|February|Feb|FEBRUARY|FEB|March|MARCH|Mar|MAR|April|APRIL|Apr|APR|May|MAY|June|JUNE|Jun|JUN|July|JULY|Jul|JUL|August|AUGUST|Aug|AUG|September|SEPTEMBER|Sep|SEP|October|OCTOBER|Oct|OCT|November|NOVEMBER|Nov|NOV|December|DECEMBER|Dec|DEC)')

# Regex that tries to pull the ull date out of the text
df['full_date'] = df.text.str.extract(r'([aA-zZ]+\b[\W]+\d+[\W+|\s]+18[\d]{2})')



#Pull out the brackets, and other odd characters from full date
df.full_date = df.full_date.str.replace('[', '')
df.full_date = df.full_date.str.replace(']', '')
df.full_date = df.full_date.str.replace('?', '')
df.full_date = df.full_date.str.replace('Jany', 'January')
df.full_date = df.full_date.str.replace('Feby', 'February')
df.full_date = df.full_date.str.replace('Febry', 'February')
df.full_date = df.full_date.str.replace('Novr', 'November')
df.full_date = df.full_date.str.replace('Decr', 'December')
df.full_date = df.full_date.str.replace('Octr', 'October')
df.full_date = df.full_date.str.replace('Augt', 'August')
df.full_date = df.full_date.str.replace(':', '.')
df.full_date = df.full_date.str.replace('---', '.')
df.full_date = df.full_date.str.replace('.', ',')

# This succesfully converts most of the dates to datetime, but I think that we can clean them up a little bit before hand by stripping out unnecessary punctuation, mapping abbreviations to full months, etc.
df['date'] = pd.to_datetime(df[df.full_date.isnull()==False].full_date, errors = 'coerce')

# Fill in some of the values that were null with the first date of the month
df.full_date.fillna(df.month+' 1, '+df.year, inplace=True)
for i in df[df.date.isnull()==True].index:
    date_creation = '%r 1, %r'%(df.iloc[i].month, df.iloc[i].year)
    df.ix[i, 'full_date'] = date_creation

# convert the dates again now that all the nulls have been filled
df['date'] = pd.to_datetime(df[df.full_date.isnull()==False].full_date, errors = 'coerce')

# We have uccessfully cleaned up the dates so that as many as we could fill have been filled.

# Drop the row values that have neither month nor year dates. Those can't be imputed. In all, we lost around 40 rows with that.
df.dropna(subset=['year'], inplace=True)
df.dropna(subset=['month'], inplace=True)
df.isnull().sum()

#Reset the index for the loop we're about to do.
df.reset_index(inplace=True)

# Load the relevant parser
nlp = spacy.load('en')

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
# Join the list of parsed texts back onto the original dataframe

parse_df = pd.DataFrame(parsed, columns = ['parsed'])
test = df.join(parse_df)
test.drop('index', axis=1, inplace=True)

# Clean up some dtypes

test['year'] = pd.to_numeric(test['year'])

for token in parse_df.iloc[1].parsed:
    if token.pos_ != 'PUNCT':
        print token.orth_, token.pos_,'\n', token.lemma_

for text in parse_df.iloc[0:100].parsed:
    print '***', len(text)
    for token in text:
        if token.pos_ == 'VERB':
            print token, token.lemma_


test.tail(20)

# add a column that has the length of each item
def text_length(doc):
    count = doc.count_by(ORTH)
    return len(count)

test['word_count'] = test['parsed'].apply(text_length)
test['stepped'] = test['date'].apply(datetime.date)


# Create a dataframe that is ordered by date, and then do some work on groupings of that.

ordered = test.sort_values('stepped', ascending=True)

ordered.reset_index(drop=True, inplace=True)

ordered['year']  = pd.to_numeric(ordered.year)
plt.scatter(ordered.year, ordered.word_count)

by_year = test.groupby('year')
plt.style.use('fivethirtyeight')
by_year.word_count.mean().plot(kind='line')
by_year.word_count.count().plot(kind='line')
plt.legend(['Average Document Length', 'Total Documents Written'], loc=2)
plt.title('Abe Lincoln: Prolificacy vs. Brevity')
plt.savefig('/Users/codylaminack/Documents/Practice/lincoln/visualization/Count_vs_length_by_year.png', bbox_inches='tight', pad_inches=0.75, Transparent=True)
plt.show()

test_date = test.ix[1].date
import datetime
def string_date(date):
    return dates.DateFormatter.strftime_pre_1900(date, "%d-%m-%Y")
# Not sure how to figure out this piece, but it'll be important to to plotting a lot of the results. Still can't figure out this microsecond answer.
# In the interest of time, I'm going to program in something that will allow me to plot time more granularly than by year.
# It's hard to say for sure, but it seems like the problem has something to do with the way the strftime function is taking in the date and converting it into a string

# oldies = dates.DateFormatter
# test_date = test.ix[1].date + datetime.timedelta(milliseconds=500)
# test_date
#
# dates.DateFormatter.strftime_pre_1900(oldies(test.ix[i].date+datetime.timedelta(milliseconds=500)), '%d/%m/%Y %f')
# oldies('1899-01-01')


# Hard coding in the months. Should be pretty simple: this column will represent what month in the century an event took place.
month = lambda x: x.month
test['month_numeric'] = test.date.apply(month)
test['months_into_century'] = ((test['year']-1800)*12)+(test['month_numeric'])

test[test.months_into_century >= 720]

# Playing around in Spacy. Referencing above-created list, "parsed"

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


for i in test.parsed.iloc[0:100]:
    print i
    for token in i:
        if token.pos_ == 'ADJ':
            print token.orth_, token.pos_

# https://github.com/cl65610/DSI-DC-2/blob/master/week-04/5.1-natural-language-processing/code/yelp_review_text_lab-solution.ipynb nlp lab with some useful code

sid = SentimentIntensityAnalyzer()
k = sid.polarity_scores(test.ix[1].text)
k

for i in range(2000,2100):
    print test.ix[i].title
    x = TextBlob(test.ix[i].text.decode('utf-8')).sentiment
    print x
    k = sid.polarity_scores(test.ix[i].text.decode('utf-8'))
    print k

# A Function that tries to pull out all of the sentiment measures we can. Kicked a "too many values to unpack" error the first time.
# def get_sentiment(doc):
#     x = TextBlob(doc.decode('utf-8')).sentiment
#     y = sid.polarity_scores(doc.decode('utf-8'))
#     return x.polarity, x.subjectivity, y['neg'], y['neu'], y['pos'], y['compound']

# test['polarity'], test['subjectivity'], test['negativity'], test['neutrality'], test['positivity'], test['compound'] = test.text.apply(get_sentiment)

def polarity(doc):
    sent = TextBlob(doc.decode('utf-8')).sentiment
    return sent.polarity

def subjectivity(doc):
    sent = TextBlob(doc.decode('utf-8')).sentiment
    return sent.subjectivity

def negativity(doc):
    return sid.polarity_scores(doc.decode('utf-8'))['neg']

negativity(test.ix[1].text)

test['polarity']= test.text.apply(polarity)
test['subjectivity'] = test.text.apply(subjectivity)

presidency_months = test[test.months_into_century >= 720].groupby('months_into_century')
labels = ['Jan 1860', 'Aug 1860', 'Jan 1861', 'Aug 1861', 'Jan 1862', 'Aug 1862',
        ' Jan 1863', 'Aug 1863', 'Jan 1864', 'Aug 1864', 'Jan 1865', 'Aug 1865']
tickrange = range(720, 800, 6)
plt.style.use('seaborn-poster')
presidency_months.polarity.mean().plot(kind='line', linewidth=1.75, color='teal')
plt.xticks(tickrange, labels, rotation = 65)
plt.xlabel('Lincoln\'s Presidency')
plt.ylabel('Average Monthly Sentiment')
plt.title('Clear and Present Feelings')
# plt.savefig('/Users/codylaminack/Documents/Practice/lincoln/visualization/pres_feelings.png', bbox_inches='tight', pad_inches=0.75, Transparent=True)
plt.show()

# This NLTK code is painfully slow. Need to find a faster way
# test['negativity'] = test.text.apply(negativity)

# Looking into some of the texts at either end of the polarity spectrum
test.ix[2418].text
test[test.polarity >=0.8]
test[test.polarity <= -0.5]

#Looking into some specific points in time
sid.polarity_scores(test.ix[4639].text.decode('utf-8'))
test[(test.title.str.contains('Mary Lincoln')) | (test.title.str.contains('Mary Todd'))]

test[test.text.str.contains('Antietam')]

sns.distplot(test[test.months_into_century >720].polarity, color='teal')
sns.distplot(test[test.months_into_century<=720].polarity, color='brown')
plt.show()
sns.distplot(test.subjectivity)

by_year.polarity.mean().plot(kind='line')
by_year.subjectivity.mean().plot(kind='line')
plt.legend()
plt.savefig('/Users/codylaminack/Documents/Practice/lincoln/visualization/subjectivity_polarity_over_time.png', bbox_inches='tight', pad_inches=0.75, Transparent=True)
plt.show()

for sent in test.ix[3000].parsed.sents:
    print sent

#  PUsh this cleaned csv so that we can begin some topic modeling on it
test.to_csv('/Users/codylaminack/Documents/Practice/lincoln/data/parsed_lincoln.csv')

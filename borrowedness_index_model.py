# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 15:43:18 2017

@author: prashanth
"""

#%%
import pandas as pd
import numpy as np
twitter_data = open('additional/Datasheet.csv').readlines()
twitter_data_tags = [i.split(',')[1::] for i in twitter_data]
twitter_data_ids = [int(i.split(',')[0]) for i in twitter_data]

twitter_data_en = []
twitter_data_hi = []
twitter_data_other = []
for k1 in twitter_data_tags:
    twitter_data_en.extend([sum(['EN' in k2 for k2 in k1])])
    twitter_data_hi.extend([sum(['HI' in k2 for k2 in k1])])
    twitter_data_other.extend([sum(['OTHER' in k2 for k2 in k1])])

twitter_data_tags_mat = np.c_[twitter_data_ids,twitter_data_en,twitter_data_hi,twitter_data_other]
twitter_data_tags_df = pd.DataFrame(twitter_data_tags_mat,columns = ['tweet_id', 'EN','HI','OTHER'])
twitter_data_tags_df['Total'] = twitter_data_tags_df.EN + twitter_data_tags_df.HI + twitter_data_tags_df.OTHER
twitter_data_tags_df['EN_per'] = twitter_data_tags_df.EN*100/twitter_data_tags_df.Total
twitter_data_tags_df['HI_per'] = twitter_data_tags_df.HI*100/twitter_data_tags_df.Total
twitter_data_tags_df['OTHER_per'] = twitter_data_tags_df.OTHER*100/twitter_data_tags_df.Total

def f(row):
    if row['EN_per'] >=90.0:
        val = 'EN'
    if row['HI_per'] >=90.0:
        val = 'HI'    
    if row['EN_per'] >=50.0:
        val = 'CM_EN'    
    elif row['HI_per'] >=50.0:
        val = 'CM_HI'    
    else:
        val = 'NA'
    return val
    
twitter_data_tags_df['Label'] = twitter_data_tags_df.apply(f, axis = 1)

#%%
twitter_data_tags_df = twitter_data_tags_df[twitter_data_tags_df['EN']>0]
twitter_data_tags_df = twitter_data_tags_df[twitter_data_tags_df['HI']>0]
twitter_data_tags_df = twitter_data_tags_df.drop_duplicates(subset = 'tweet_id')

#%%
twitter_data_df = pd.read_csv('additional/Datasheet_tweets_clean.csv')
twitter_data_df = twitter_data_df.drop_duplicates(subset = 'tweet_id')
twitter_data_df = twitter_data_df.merge(twitter_data_tags_df,how ='inner', left_on = 'tweet_id',right_on = 'tweet_id')
#%%
from nltk.tokenize import word_tokenize
from collections import Counter
import re
from nltk.corpus import stopwords
import string
 
stop = stopwords.words('english') 

def remove_non_ascii_1(text):
    return ''.join(i for i in text if ord(i)<128)

tweet_text = [remove_non_ascii_1(text) for text in twitter_data_df.tweet]
# remove urls
tweet_text = [re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', text) for text in tweet_text]
# remove punctuations
regex = re.compile('[%s]' % re.escape(string.punctuation)) # reg exprn for puntuation
tweet_text = [regex.sub(' ', text) for text in tweet_text]

terms_all = []
for i in tweet_text:
    terms_all.extend([term for term in word_tokenize(i.lower()) if term not in stop])

tweet_count = Counter(terms_all).most_common()
tweet_token_count_df = pd.DataFrame(tweet_count, columns=['Word', 'term_frequency'])

#%%
test_words = open('input.txt').readlines()
test_words = [text.replace('\r\n','') for text in test_words]
test_words_df = pd.DataFrame(test_words,columns=['Word'])
test_words_tf_df = tweet_token_count_df.merge(test_words_df,how ='inner', left_on = 'Word',right_on = 'Word')

#%%
from translate import Translator
translator= Translator(to_lang="hi")
#print translator.translate("sir")

test_words_to_hi = []
ascii_letters = string.ascii_letters
ascii_letters = [x for x in ascii_letters]
for word in test_words:
    hi_word = translator.translate(word)
    hi_word = ''.join([i for i in hi_word if i not in string.punctuation])
    hi_word2 = [x for x in hi_word]
    if len(set(hi_word2).intersection(set(ascii_letters))) == 0:
        test_words_to_hi.append(hi_word)
    else:
        test_words_to_hi.append('')
    print hi_word
test_words_to_hi_ = []
for word in test_words_to_hi:
    if len(word.split()) == 1:
        test_words_to_hi_.append(word)
    else:
        test_words_to_hi_.append('')
#%%
import re
from transliteration import Transliterator
tr = Transliterator()
#tr.transliterate_xx_en(u'महोदय',"hi_IN")

test_words_hi_en = []
for word in test_words_to_hi_:
    try:
        test_words_hi_en.append(re.sub(r'[^\x00-\x7F]+','', tr.transliterate_xx_en(word,"hi_IN")))
    except:
        test_words_hi_en.append('')
    
#%%
import re
import string    
test_words_to_hi2 = pd.DataFrame(np.c_[test_words,test_words_to_hi_,test_words_hi_en],columns = ['Word_EN', 'Word_HI','Word_HI2'])

#%%
test_words_to_hi3 = pd.merge(tweet_token_count_df,test_words_to_hi2,how ='right', 
         left_on = 'Word',right_on = 'Word_EN')
test_words_to_hi3.columns.values[1] = 'term_frequency_en'
test_words_to_hi4 = pd.merge(tweet_token_count_df,test_words_to_hi2,how ='right', 
         left_on = 'Word',right_on = 'Word_HI2') 
test_words_to_hi4.columns.values[1] = 'term_frequency_hi'         
test_words_to_hi5 = pd.merge(test_words_to_hi3,test_words_to_hi4[['Word_EN','term_frequency_hi']],how ='right', 
         left_on = 'Word_EN',right_on = 'Word_EN')         
test_words_to_hi5 = test_words_to_hi5[['Word_EN','term_frequency_en','Word_HI','Word_HI2','term_frequency_hi']]
test_words_to_hi5 = test_words_to_hi5.fillna(0)
test_words_to_hi5.loc[test_words_to_hi5.Word_HI2 == test_words_to_hi5.Word_EN,'term_frequency_hi'] = 0
test_words_to_hi5['Score'] = (test_words_to_hi5.term_frequency_en)/(test_words_to_hi5.term_frequency_hi+1)
test_words_ranking = test_words_to_hi5[['Word_EN', 'Score']].sort_values(by= 'Score',ascending = False)
test_words_ranking['Rank'] = range(1,len(test_words_ranking)+1)
test_words_ranking[['Word_EN', 'Rank']].to_csv('output.csv', index = False)
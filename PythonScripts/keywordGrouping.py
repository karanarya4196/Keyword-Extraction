import pymysql
import pandas as pd
import re
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')
from Spacy_Tagging import getPosTaggedData
from Wordnet_functionality import getPathSimilarity, get_rootword, isWordPresentInWordnet, isAnyWordNotPresentInWordnetCheck
import wikipedia
import json
import time
import glob
import os
from ast import literal_eval
from tqdm import tqdm
import operator
from nltk import word_tokenize, pos_tag
from itertools import combinations as cb
import warnings
warnings.filterwarnings("ignore")


def penn_to_wn(tag):

    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None

def get_synsets(sentence):
    synsets = [tagged_to_synset(*tagged_word) for tagged_word in sentence]
    synsets = [ss for ss in synsets if ss]
    return synsets

def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None

def sentence_similarity(synsets1, synsets2):

    score, count = 0.0, 0
    for synset in synsets1:        
        score = 0
        count = 0
        for ss in synsets2:
            score_int = synset.path_similarity(ss)
            if score_int!=None and score_int>score:
                score+=score_int
                count+=1

    if count == 0:
        return 0

    return score/count
    
    
def arrangeKeywordGroupsDataFrame(keywords_list, results, date_time, catId):
    master_keyword_dict = {}
    for keywords, result in zip(keywords_list, results):
        text = result['sectionText'].lower()
        keywords = list(set(keywords))
        
        for keyw in keywords:
            keyw = keyw.lower()
            keyw = keyw.strip()
            if keyw in master_keyword_dict.keys():
                previous_count = master_keyword_dict[keyw]
                master_keyword_dict[keyw] = previous_count + text.count(keyw)
            else:
                master_keyword_dict.update({keyw: text.count(keyw)})

    sorted_x = sorted(master_keyword_dict.items(), key=operator.itemgetter(1), reverse = True)
    df = pd.DataFrame(sorted_x)
    df.columns = ['Keywords', 'Frequency']
    count_keywords_df = df.copy()
    master_list_update = [item for item in master_keyword_dict.keys() if len(item.split(' ')) > 1]


    remove_list = []
    for keyw in master_keyword_dict.keys():
        if (len(keyw.split(' '))) == 1:
            for item in master_list_update:
                if keyw in item:
                    remove_list.append(keyw)

    remove_list = list(set(remove_list))

    for key in remove_list:
        if key in master_keyword_dict.keys():
            del master_keyword_dict[key]
            

    sorted_x = sorted(master_keyword_dict.items(), key=operator.itemgetter(1), reverse = True)
    df = pd.DataFrame(sorted_x)
    df.columns = ['Keywords', 'Frequency']
    df['Keyword_Length'] = df['Keywords'].str.split(' ').apply(lambda x: len(x))
    new_df = df[df['Keyword_Length'] > 1]


    helping_words = ('purposes', 'others', 'its', 'given', 'will', 'following', 'doing', 'using', 'that', 'which', 'do', 'use', 'used',
    'are', 'existing', 'has', 'make', 'means', 'shall', 'making', 'been', 'own', 'inch', 'was', 'should', 'be', 'in', 'is', 'same', 'their',
    'first', 'such', 'his', 'a', 'or', 'would', 'based', 'other', 'who', 'were', 'gave', 'e', 'am', 'give', 'good', 'et', 'did', 'her', 'have',
    'being', 'makes', 'day', 'does', 'due', 'had', 'whose', 'said')

    helping_words_pattern = '|'.join(helping_words)

    start_regex_pattern = r'^(' + helping_words_pattern + r')\b'
    end_regex_pattern = r'\b(' + helping_words_pattern + r')$'

    new_df = new_df[~(new_df['Keywords'].str.contains(start_regex_pattern, regex = True))]
    new_df = new_df[~(new_df['Keywords'].str.contains(end_regex_pattern, regex = True))]  
    new_df = new_df[~(new_df['Keywords'].apply(lambda x : bool(re.search(r'\d', x))) == True)]

    stops = stopwords.words('english')
    new_df['isStopWordsPresent'] = new_df['Keywords'].apply(lambda x: 'Yes' if any(word in stops for word in x.split(' ')) else 'No')
    new_df['isStopWordsPresent'].value_counts()
    new_df['Last_keyword'] = new_df['Keywords'].str.split(' ').apply(lambda x: x[-1])

    action_noun_list = []
    for word in new_df['Last_keyword']:
        lexname_list = []
        for synset in wn.synsets(word):
            if synset.name().split(".")[1]=="n":
                lexname_list.append(synset.lexname())
        if len(lexname_list) == 0:
            action_noun_list.append('No')
            continue
        elif lexname_list[0] == 'noun.act':
            action_noun_list.append('Yes')
            continue
        elif ((len(lexname_list) >= 4) & ((lexname_list.count('noun.act')*100/len(lexname_list)) >= 40)):
            action_noun_list.append('Yes')
            continue
        else:
            action_noun_list.append('No')
            continue

    new_df['Action Noun'] = action_noun_list
    result = new_df[new_df['Action Noun'] == "Yes"]
    result = result[(result['Frequency'] > 0)]
    result = result[result['isStopWordsPresent'] == 'No']

    result = result.sort_values(by = 'Keyword_Length', ascending = False)
    sentence_list = result['Keywords'].tolist()

    sentence_dict = {}
    for sentence in sentence_list:
        sentence_dict[sentence] = get_synsets(pos_tag(word_tokenize(sentence)))

    sentence_cluster_dict = {}

    for sentence in sentence_dict:
        sentence_pos = sentence_dict[sentence]
        if len(sentence_cluster_dict)>0:
            isFound=False
            for sentence_cluster in sentence_cluster_dict.keys():
                for s in sentence_cluster_dict[sentence_cluster]:
                    if sentence_similarity(sentence_pos, sentence_dict[s]) > 0.5:
                        sentence_cluster_dict[sentence_cluster].append(sentence)
                        isFound = True
                        break
                if isFound:
                    break
            if not isFound:
                sentence_cluster_dict[sentence] = [sentence]
        else:
            sentence_cluster_dict[sentence] = [sentence]

    final_master_list = []

    for sublist in list(sentence_cluster_dict.values()):
        for item in sublist:
            final_master_list.append(item)

    count_list = []

    for item in list(sentence_cluster_dict.values()):
        count_list.append(len(item))

    answer = pd.DataFrame({'Cluster': list(sentence_cluster_dict.values()),
                'Size of Cluster': count_list})
    answer = answer.sort_values(by = 'Size of Cluster', ascending = False)
    answer = answer[['Size of Cluster', 'Cluster']]
    max_cluster_size = int(answer['Size of Cluster'][0:1])
    answer['Cluster'] = answer['Cluster'].apply(lambda x: (x + [''] * (max_cluster_size - len(x))))
    answer[['Word_{}'.format(i) for i in range(1, (max_cluster_size + 1), 1)]] = pd.DataFrame(answer.Cluster.values.tolist(), index= answer.index)

    remove_list = []
    updated_item_list = []
    for item_list in answer['Cluster']:
        item_list = [item for item in item_list if item != '']
        item_list.sort(key = lambda x: len(x.split(' ')), reverse = True)
        for item1, item2 in cb(item_list, 2):
            if item1 not in remove_list and item2 not in remove_list:
                if (sentence_similarity(sentence_dict[item1], sentence_dict[item2])) > 0.7:
                    remove_list.append(item2)
        new_item_list = [item for item in item_list if item not in remove_list]
        updated_item_list.append(new_item_list)

    count_list = []
    for item in updated_item_list:
        count_list.append(len(item))

    updated_answer = pd.DataFrame({'Cluster': updated_item_list,
                'Size of Cluster': count_list})
    updated_answer = updated_answer.sort_values(by = 'Size of Cluster', ascending = False)
    updated_answer = updated_answer[['Size of Cluster', 'Cluster']]
    max_updated_cluster_size = int(updated_answer['Size of Cluster'][0:1])
    updated_answer['Cluster'] = updated_answer['Cluster'].apply(lambda x: (x + [''] * (max_updated_cluster_size - len(x))))
    updated_answer[['Word_{}'.format(i) for i in range(1, max_updated_cluster_size + 1, 1)]] = pd.DataFrame(updated_answer.Cluster.values.tolist(), index = updated_answer.index)
    updated_answer = updated_answer.drop(columns = ['Cluster'])
    updated_answer.to_excel('../Output/CatId_{}_Keywords_'.format(catId) + date_time + '/UntrainedKeywordGroups.xlsx', index = False)
    return count_keywords_df, updated_answer
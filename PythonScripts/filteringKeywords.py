import pandas as pd
import re
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import nltk
from Spacy_Tagging import getPosTaggedData
from Wordnet_functionality import getPathSimilarity, get_rootword, isWordPresentInWordnet, isAnyWordNotPresentInWordnetCheck
import wikipedia
import json
import time
import glob
import os
import numpy as np
from nltk.stem import WordNetLemmatizer, PorterStemmer
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")



def getSimilarity(phrase1_lst, phrase2_lst):    
    sim_val_lst = []
    for word in phrase1_lst:
        max_sim = 0
        for word_temp in phrase2_lst:
            if get_rootword(word, 'NN') == get_rootword(word_temp, 'NN'):
                sim_val_temp = 1
            else:
                if word in sim_dict and word_temp in sim_dict[word]:
                    sim_val_temp = sim_dict[word][word_temp]
                else:
                    sim_val_temp = getPathSimilarity(word, word_temp)
                    if word in sim_dict:
                        sim_dict[word][word_temp] = sim_val_temp
                    else:
                        sim_dict[word] = {word_temp:sim_val_temp}
                        
            if sim_val_temp > max_sim:
                max_sim = sim_val_temp
                
        sim_val_lst.append(max_sim)
    
    return_val = float(sum(sim_val_lst)) / float(len(sim_val_lst))
        
    return return_val

sim_dict = {}
def filteringKeywordsUsingReferenceList(keyword_list, reference_list, df, threshold, date_time, catId):
    
    main_keyword_list = []

    for item_list in keyword_list:
        for word in item_list:
            main_keyword_list.append(word)

    main_keyword_list = list(set(main_keyword_list))
    reference_list = [item.lower() for item in reference_list]   
    reference_list = [re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', item) for item in reference_list]
    reference_list = list(set(reference_list))
    
    
    updated_keyword_list = []
    for keyword in main_keyword_list:
        isFound = False
        for reference_word in reference_list:
            if getSimilarity(str(keyword).split(), str(reference_word).split()) > threshold:
                updated_keyword_list.append(keyword)
                isFound=True
                break
            
    updated_keyword_list = list(set(updated_keyword_list))
    updated_keyword_list = [item.lower() for item in updated_keyword_list]
    updated_keyword_list = list(set(updated_keyword_list))

    phrases_list = []
    for phrase in updated_keyword_list:
        if len(phrase.split()) > 1:
            phrases_list.append(phrase)

    stemmer = PorterStemmer()

    remove_words = []
    for phrase in updated_keyword_list:
        if len(phrase.split()) == 1:
            for multi_phrase in phrases_list:
                if stemmer.stem(phrase) in multi_phrase:
                    remove_words.append(phrase)
                    break
                    
    for keyword in updated_keyword_list:
        if keyword in remove_words:
            updated_keyword_list.remove(keyword)

    customStopWords = ['that', 'which', 'its', 'be', 'own', 'is', 'or', 'their', 'other', 'in', 'day', 'make', 'same',
    'makes', 'such', 'use','e', 'do', 'his', 'her', 'inch', 'a', 'has', 'shall']

    helping_words = ('purposes', 'others', 'its', 'given', 'will', 'following', 'doing', 'using', 'that', 'which', 'do', 'use', 'used',
    'are', 'existing', 'has', 'make', 'means', 'shall', 'making', 'been', 'own', 'inch', 'was', 'should', 'be', 'in', 'is', 'same', 'their',
    'first', 'such', 'his', 'a', 'or', 'would', 'based', 'other', 'who', 'were', 'gave', 'e', 'am', 'give', 'good', 'et', 'did', 'her', 'have',
    'being', 'makes', 'day', 'does', 'due', 'had', 'whose', 'said')

    helping_words_pattern = '|'.join(helping_words)

    start_regex_pattern = r'^(' + helping_words_pattern + r')\b'
    end_regex_pattern = r'\b(' + helping_words_pattern + r')$'

    remove_additional = []
    for phrase in updated_keyword_list:
        if (bool(re.match(start_regex_pattern, phrase))):
            remove_additional.append(phrase)
            continue
        if (bool(re.match(end_regex_pattern, phrase))):
            remove_additional.append(phrase)
            continue

    for word in remove_additional:
        updated_keyword_list.remove(word)

    remove_additional = []
    for phrase in updated_keyword_list:
        word_list = phrase.split()
        for word in word_list:
            if len(word) < 3:
                remove_additional.append(phrase)
                break
        
    for word in remove_additional:
        updated_keyword_list.remove(word)

    df[df['Keywords'].isin(updated_keyword_list)].to_excel('../Output/CatId_{}_Keywords_'.format(catId) + date_time + '/FinalTrainedKeywords.xlsx', index = False)
    return updated_keyword_list
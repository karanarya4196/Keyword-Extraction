import pandas as pd
import re
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')
from Spacy_Tagging import getPosTaggedData
from Wordnet_functionality import getPathSimilarity, get_rootword, isWordPresentInWordnet, isAnyWordNotPresentInWordnetCheck
import json
import time
import glob
import os
from ast import literal_eval
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")


NN_GRP = r'([A-Za-z\d]+/(ADJ) )?(([A-Za-z\d\-]+/(NOUN) )+)?[A-Za-z\d\-]+/(NOUN)'
VB_NN_GRP = r'([A-Za-z\d]+/(VERB) )([A-Za-z\d]+/(ADJ) )?(([A-Za-z\d\-]+/(NOUN) )+)?[A-Za-z\d\-]+/(NOUN)'
VB_PREP_NN_GRP = r'([A-Za-z\d]+/(VERB) )([A-Za-z\d]+/(ADJ) )?([A-Za-z\d\-]+/(ADP|DET|CONJ) )(([A-Za-z\d\-]+/(NOUN) )+)?[A-Za-z\d\-]+/(NOUN)'
NN_PREP_NN_GRP_UPDATED = r'([A-Za-z\\d]+/ADJ )?(([A-Za-z\\d\\-]+/NOUN )+)(([A-Za-z\\d\\-]+/(ADP|DET|CONJ) )+)(([A-Za-z\\d\\-]+/(NOUN) )+)?[A-Za-z\\d\\-]+/(NOUN)'
VB_ADV_VB_GRP = r'(([A-Za-z\\d]+/(VERB)( |))+)(([A-Za-z\\d\-]+/(ADJ)( |))+)?(([A-Za-z\\d\-]+/(PUNCT)( |))+)?([A-Za-z\\d\-]+/(ADV|ADJ)( |))(([A-Za-z\\d\-]+/(PUNCT)( |))+)?(([A-Za-z\\d\-]+/(ADJ|NOUN|VERB)( |))+)(([A-Za-z\\d\-]+/(PUNCT)( |))+)?(([A-Za-z\\d\\-]+/(NOUN)( |))+)?[A-Za-z\\d\\-]+/(NOUN)'
NN_VB_NN_GRP = r'(([A-Za-z\\d\\-]+/(NOUN) )+)?[A-Za-z\\d\\-]+/(NOUN) ([A-Za-z\\d]+/(VERB) )(([A-Za-z\\d\\-]+/(ADP|CONJ|DET) )+)?([A-Za-z\\d]+/(ADJ) )?(([A-Za-z\\d\\-]+/(NOUN) )+)?[A-Za-z\\d\\-]+/(NOUN)'

def getTextFromPOSData(data):
    return ' '.join([d.split('/')[0] for d in data.split(' ')])

def doPOSTaggingOnText(text_arr):
    document_text_temp_pos_temp = []
    for paragraph in text_arr:
        temp_list = []
        for line in nltk.sent_tokenize(paragraph):
            temp_list.append(getPosTaggedData(line))
        document_text_temp_pos_temp.append(temp_list)
    return document_text_temp_pos_temp

def getKeywordListInSentence(document_temp_pos, pattern):
    word_dict_temp = {}
    for pos_tagged in document_temp_pos:
        for line in pos_tagged:
            if len(line.split(' ')) > 5:
                for c in re.finditer(pattern, line):
                    phrase = getTextFromPOSData(c.group())
                    if phrase.lower() not in stop_word_list:
                        text = getTextFromPOSData(phrase)
                        if text in word_dict_temp:
                            word_dict_temp[text] = word_dict_temp[text] + 1
                        else:
                            word_dict_temp[text] = 1                       
    return word_dict_temp

stop_word_list = stopwords.words("english")

def createOutputDictionary(document_name_temp):
    final_output_dict_temp = {}
    temp_dict = {}
    temp_dict['Acronym'] = []
    temp_dict['Laws_Rules_Acts_Regulations'] = []
    temp_dict['VB_NN_Phrase'] = []
    temp_dict['NN_Phrase'] = []
    final_output_dict_temp[document_name_temp] = temp_dict
    
    return final_output_dict_temp


def extractPhrases(pos_text, doc_name):
    content_NN_GRP_dict = {}
    content_VB_NN_GRP_dict = {}
    content_NN_PREP_NN_GRP_dict = {}
    content_VB_PREP_NN_GRP_dict = {}
    content_VB_ADV_VB_GRP_dict = {}
    content_NN_VB_NN_GRP_dict = {}
    content_NN_VB_NN_GRP_dict = {}
    
    word_dict = getKeywordListInSentence(pos_text, NN_GRP)
    content_NN_GRP_dict[doc_name] = word_dict
    
    word_dict = getKeywordListInSentence(pos_text, VB_NN_GRP)
    content_VB_NN_GRP_dict[doc_name] = word_dict
      
    word_dict = getKeywordListInSentence(pos_text, VB_PREP_NN_GRP)
    content_VB_PREP_NN_GRP_dict[doc_name] = word_dict
    
    word_dict = getKeywordListInSentence(pos_text, NN_PREP_NN_GRP_UPDATED)
    content_NN_PREP_NN_GRP_dict[doc_name] = word_dict

    word_dict = getKeywordListInSentence(pos_text, VB_ADV_VB_GRP)
    content_VB_ADV_VB_GRP_dict[doc_name] = word_dict

    word_dict = getKeywordListInSentence(pos_text, NN_VB_NN_GRP)
    content_NN_VB_NN_GRP_dict[doc_name] = word_dict
    
    return content_VB_NN_GRP_dict, content_NN_GRP_dict, content_NN_PREP_NN_GRP_dict, content_VB_PREP_NN_GRP_dict, content_VB_ADV_VB_GRP_dict, content_NN_VB_NN_GRP_dict

def extractKeywords(document_text_temp, document_name):
    
    document_text_temp = "\n".join([re.sub('[\s]+', ' ', line) for line in document_text_temp.split('\n') if len(re.sub('[\s]+', ' ', line).strip())>0])
    document_text_temp = document_text_temp.split('\n')

    document_text_temp_pos = doPOSTaggingOnText(document_text_temp)

    content_VB_NN_GRP_dict, content_NN_GRP_dict, content_NN_PREP_NN_GRP_dict, content_VB_PREP_NN_GRP_dict, content_VB_ADV_VB_GRP_dict, content_NN_VB_NN_GRP_dict = extractPhrases(document_text_temp_pos, document_name)
    return content_VB_NN_GRP_dict, content_NN_GRP_dict, content_NN_PREP_NN_GRP_dict, content_VB_PREP_NN_GRP_dict, content_VB_ADV_VB_GRP_dict, content_NN_VB_NN_GRP_dict


def generateKeywords(results):

    keywords_per_document_list = []
    keywords_all_documents_list = []

    for result in results:
        
        document_text = result['sectionText']
        document_text = document_text.replace('\n', '')
        document_name = re.sub(r'[^a-zA-Z0-9 \n\.]', '_', result['citation'])
        
        content_VB_NN_GRP_dict, content_NN_GRP_dict, content_NN_PREP_NN_GRP_dict, content_VB_PREP_NN_GRP_dict, content_VB_ADV_VB_GRP_dict, content_NN_VB_NN_GRP_dict = extractKeywords(document_text, document_name)

        master_list = list(content_VB_NN_GRP_dict[document_name].keys()) + list(content_NN_GRP_dict[document_name].keys()) + list(content_NN_PREP_NN_GRP_dict[document_name].keys()) + list(content_VB_PREP_NN_GRP_dict[document_name].keys()) + list(content_VB_ADV_VB_GRP_dict[document_name].keys()) + list(content_NN_VB_NN_GRP_dict[document_name].keys())
        
        master_list_update = [item for item in master_list if len(item.split(' ')) > 1]
        list_list = [item.split(' ') for item in master_list_update]
        final_master_list_update = [item for sublist in list_list for item in sublist]

        for item in master_list:
            if len(item.split(' ')) == 1:
                if item in final_master_list_update:
                    master_list.remove(item)
                    
                    
        master_list = [item for item in master_list if len(item) > 3]
        keywords_per_document_list.append(master_list)


        keywords_master_list = list(list(content_NN_GRP_dict[document_name].keys()) + list(content_VB_NN_GRP_dict[document_name].keys()))
        
        keywords_master_list_update = [item for item in keywords_master_list if len(item.split(' ')) > 1]
        keywords_list_list = [item.split(' ') for item in keywords_master_list_update]
        final_keywords_master_list_update = [item for sublist in keywords_list_list for item in sublist]

        for item in keywords_master_list:
            if len(item.split(' ')) == 1:
                if item in final_keywords_master_list_update:
                    keywords_master_list.remove(item)
                    
                    
        keywords_master_list = [item for item in keywords_master_list if len(item) > 3]
        keywords_all_documents_list.append(keywords_master_list)

    return keywords_per_document_list, keywords_all_documents_list

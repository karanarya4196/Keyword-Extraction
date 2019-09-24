import pickle
import pysolr
import json
import pandas as pd
import re
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import nltk
import spacy
nlp = spacy.load('en_core_web_lg')
from Spacy_Tagging import getPosTaggedData
from Wordnet_functionality import getPathSimilarity, get_rootword, isWordPresentInWordnet, isAnyWordNotPresentInWordnetCheck
import time
import glob
import os
from ast import literal_eval
from collections import defaultdict
from initialize import *
from keywordGenerator import *
from keywordGrouping import *
from filteringKeywords import *
from generateHTML import *
import warnings
warnings.filterwarnings("ignore")


# Start time
start_time = datetime.datetime.now()
print('Extraction of keywords started at', start_time)

# Running initialization function
date_time, catId, variables, results, catIdResults = initialization()

# Generating exhaustive for every document and master keywords for all documents
print('Keywords extraction for catId {} started!'.format(catId))
keywords_per_document_list, keywords_all_documents_list = generateKeywords(catIdResults)
print('Keywords extraction for catId {} completed!'.format(catId))

# Generating an untrained master keyword list arranged into groups with high similarity
print('Grouping of keywords for catId {} started!'.format(catId))
count_keywords_df, updated_keywords_catId_df = arrangeKeywordGroupsDataFrame(keywords_all_documents_list, catIdResults, date_time, catId)

untrained_keyword_list = []
for item in np.array(updated_keywords_catId_df.iloc[:, 1:]):
    for word in item:
        untrained_keyword_list.append(word)
untrained_keyword_list = list(set(untrained_keyword_list))
untrained_keyword_list = [word for word in untrained_keyword_list if word is not np.nan]
untrained_keyword_list = [word for word in untrained_keyword_list if len(word) > 1]
print('Grouping of keywords for catId {} completed!'.format(catId))

# Filtering the master keywords for all documents "keywords_all_documents_list" using a reference list provided by SME
print('Filtering of keywords using reference list for catId {} started!'.format(catId))
reference_list = variables[0]['referenceList']
threshold = variables[0]['threshold']
filtered_keyword_list = filteringKeywordsUsingReferenceList(keywords_all_documents_list, reference_list, count_keywords_df, threshold, date_time, catId)
print('Filtering of keywords using reference list for catId {} completed!'.format(catId))

# Highlighting the extracted keywords by creating a basic HTML UI experience
print('Highlighting keywords for catId {} started!'.format(catId))
highlightKeywordsInText(filtered_keyword_list, catIdResults, 'HighlightedFilteredKeywords', date_time, catId)
highlightKeywordsInText(untrained_keyword_list, catIdResults, 'HighlightedMasterDumpKeywords', date_time, catId)
print('Highlighting keywords for catId {} completed!'.format(catId))

# End time
print('Total time taken for extracting keywords of catId {} is'.format(catId), datetime.datetime.now() - start_time)
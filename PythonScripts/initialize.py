import re
import datetime
import os
import pickle
import pysolr
import json
import warnings
warnings.filterwarnings("ignore")


def initialization():

    # Loading the variables from Properties file
    with open('../UserFolder/Input.json') as file:
        variables = json.load(file)
    print('Input file loaded!')


    # Creating Output Directory
    date_time = re.sub(r'(\s+|-|:)', '_', str(datetime.datetime.now()).split('.')[0])
    dirName = '../Output/CatId_{}_Keywords_'.format(variables[0]['catId']) + date_time
    filteredDirName = dirName + '/HighlightedFilteredKeywords'
    masterDumpDirName = dirName + '/HighlightedMasterDumpKeywords'
    try:
        os.mkdir(dirName)
        print("Directory ", dirName,  " Created!") 
        os.mkdir(filteredDirName)
        print("Directory ", filteredDirName,  " Created!") 
        os.mkdir(masterDumpDirName)
        print("Directory ", masterDumpDirName,  " Created!") 
    except FileExistsError:
        print("Directory ", dirName ,  " already exists!")
        print("Directory ", filteredDirName ,  " already exists!")
        print("Directory ", masterDumpDirName ,  " already exists!")

    # Loading all citations which contain categoryID
    with open('../Data/documentCorpus.pickle', 'rb') as file:
        results = pickle.load(file)
    print('All citations loaded!')
    print('Total number of citations which contain categoryID are:', len(results))

    # Loading the required Category ID
    catId = variables[0]['catId']
    with open('../Data/catId_{}.pickle'.format(str(catId)), 'rb') as file:
        catIdResults = pickle.load(file)
    print('Citations of catId {} loaded!'.format(catId))
    print('Total number of citations in catID {} are:'.format(catId), len(catIdResults))

    return date_time, catId, variables, results, catIdResults
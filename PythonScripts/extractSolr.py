import pysolr
import json
import pickle

# Extracting all citations from Solr
solr = pysolr.Solr('http://ny12srvgrc7dch2:8093/solr/citation/')
results = []
for index in range(0, 67000, 1000):
    results.append(solr.search('*:*', rows = 1000, start_row = index))
    
print('Total number of citations extracted from Solr:', len(results))

with open('../Data/masterDocumentCorpus.pickle', 'wb') as file:
    pickle.dump(results, file, protocol = pickle.HIGHEST_PROTOCOL)

# Extracting all the citations which have categoryID
new_results = []
for result in results:
    if 'catId' in result.keys():
        new_results.append(result)
print('Total number of citations with categoryID:', len(new_results))

with open('../Data/documentCorpus.pickle', 'wb') as file:
    pickle.dump(new_results, file, protocol = pickle.HIGHEST_PROTOCOL)


# Extracting the citations for every categoryID
catId_list = []
for result in new_results:
    catId_list.extend(result['catId'])
catId_list = list(set(catId_list))
print('Number of unique category IDs:', len(catId_list))

solr = pysolr.Solr('http://ny12srvgrc7dch2:8093/solr/citation/')
for catId in catId_list:
    results = solr.search('catId:{}'.format(str(catId)), rows = 67000)
    with open('../Data/catId_{}.pickle'.format(str(catId)), 'rb') as file:
        pickle.dump(results, file)
    print('Results of category {} extracted from Solr!'.format(catId))
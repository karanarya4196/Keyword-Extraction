
# coding: utf-8

# ### Importing libraries

# In[2]:


from nltk.corpus import wordnet as wn


# In[3]:


def getSynonyms(word):
    synonyms = [] 
    #antonyms = []  
    for syn in wn.synsets(word): 
        for l in syn.lemmas(): 
            synonyms.append(l.name()) 
            #if l.antonyms(): 
            #    antonyms.append(l.antonyms()[0].name()) 
    return synonyms

getSynonyms('loan')


# In[16]:


def get_rootword(word, pos):
    returnWord = ''
    word = word.lower()
    if 'NN' in pos or 'NOUN' in pos:
        returnWord =  wn.morphy(word, wn.NOUN)
    elif 'VB' in pos or 'VERB' in pos:
        returnWord =  wn.morphy(word, wn.VERB)
    elif 'RB' in pos or 'ADV' in pos:
        returnWord =  wn.morphy(word, wn.ADV)
    elif 'JJ' in pos or 'ADJ' in pos:
        returnWord =  wn.morphy(word, wn.ADJ)
    
    if returnWord == None:
        return word
    
    return returnWord

get_rootword('discouraging', 'VERB')


# In[10]:


bankingAndFinanceKeywordList = set(['money', 'payment', 'loan', 'banking', 'finance', 'bank', 'debt', 'credit',
                                   'balance'])

def isWordAssociatedWithBankingOrFinanceDomain(word):
    # Checking at root level
    for node in wn.synsets(word):
        #print(node.definition())
        if len(set(node.definition().split(' ')) & bankingAndFinanceKeywordList)>0:
            return True
    
    # Checking derivationally related form
    for lemma in wn.synsets(word)[0].lemmas():
        for der_rel_form in lemma.derivationally_related_forms():
            definition = der_rel_form.synset().definition()
            if len(set(definition.split(' ')) & bankingAndFinanceKeywordList)>0:
                return True
            
    # Checking inherited hypernym tree
        
    return False


# In[12]:


#print('investment\t', isWordAssociatedWithBankingOrFinanceDomain('investment'))
#print('purchases\t', isWordAssociatedWithBankingOrFinanceDomain('purchases'))


#print('death\t\t', isWordAssociatedWithBankingOrFinanceDomain('death'))
#print('pledge\t\t', isWordAssociatedWithBankingOrFinanceDomain('pledge'))
#print('amortizing\t', isWordAssociatedWithBankingOrFinanceDomain('amortizing'))
#print('rates\t', isWordAssociatedWithBankingOrFinanceDomain('rates'))
#print('overdraft\t', isWordAssociatedWithBankingOrFinanceDomain('overdraft'))


# In[80]:


def isWordPresentInWordnet(word):
    if len(wn.synsets(word))>0:
        return True
    else:
        return False
    
## Checking if any word in the phrase is not present in wordnet
def isAnyWordNotPresentInWordnetCheck(phraseTemp):
    isAnyWordNotPresentInWordnet = False
    for wordSplit in phraseTemp.split(' '):
        if not isWordPresentInWordnet(wordSplit):
            for wordSplitSplit in wordSplit.split('-'):
                if not isWordPresentInWordnet(wordSplitSplit):
                    isAnyWordNotPresentInWordnet = True
                    break
            #isAnyWordNotPresentInWordnet = True
            break
    return isAnyWordNotPresentInWordnet


# ### Create two methods 
#     1. Get Noun form of the verb
#     2. Get hypernym tree
#     3. Check if the noun is action noun or not

# In[3]:


def getNounFormOfVerb(word):
    word = get_rootword(word, 'VERB')
    noun_list = []
    wn.synsets(word)[0].pos() == 'v'
    no_of_sense = 0
    for synset_ in wn.synsets(word):
        if synset_.pos() == 'v':
            no_of_sense+=1
            for lemma in synset_.lemmas():
                for derived_form in lemma.derivationally_related_forms():
                    #print(derived_form.name(), word)
                    if derived_form.synset().pos() == 'n' and ( derived_form.name().startswith(word) or derived_form.name().startswith(word[0:len(word)-1]) or
                            derived_form.name().startswith(word[0:len(word)-2]) ):
                        #print(derived_form)
                        noun_list.append(derived_form.name())
                        #print(derived_form.name())
        ## Considering only first sense
        if no_of_sense==1:
            break

    return noun_list

#getNounFormOfVerb(word = 'required')


# In[1]:


# word = 'requirement'
# tree_string = ''
# for s in wn.synsets(word):
#     if s.pos()=='n' and s.name().split('.')[0] == word:
#         #print(s)
#         text = s
#         while True:
#             print(text)
#             tree_string += str(text.name()) + '\n'
#             text = text.hypernyms()[0]
#             if text.name().startswith('entity'):
#                 break


# In[19]:


def getPathSimilarity(word1, word2):
    word_1_lst = []
    for synset in wn.synsets(word1):
        if synset.name().startswith(word1) or synset.name().startswith(get_rootword(word1, 'NN')):
            word_1_lst.append(synset)
            
    word_2_lst = []
    for synset in wn.synsets(word2):
        if synset.name().startswith(word2) or synset.name().startswith(get_rootword(word2, 'NN')):
            word_2_lst.append(synset)
    largest_distance = 0
    for synset1 in word_1_lst:
        for synset2 in word_2_lst:
            distance = wn.path_similarity(synset1, synset2)
            if distance!=None and distance > largest_distance:
                largest_distance = distance

    return largest_distance

getPathSimilarity('calls', 'telephone')


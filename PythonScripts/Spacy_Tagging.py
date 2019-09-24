
# coding: utf-8

# In[1]:


import spacy
from spacy import displacy
import re
import nltk


# In[2]:


nlp = spacy.load('en_core_web_lg')


# In[7]:


# doc=nlp(u'hello')
# b=doc.to_bytes()


# #### This method will return POS tagged data
#     * Format will be word1/POS word2/POS word3/POS

# In[3]:


def getPosTaggedData(sent):
    posSent = ''
    doc = nlp(sent)
    posSent = " ".join([token.text + '/' +token.pos_ for token in doc])
    return posSent


# In[38]:


#text = 'Apple is looking at buying U.K. startup for $1 billion'
#text = 'Wealth management is an investment-advisory discipline which incorporates financial planning, investment portfolio management and a number of aggregated financial services offered by a complex mix of asset managers, custodial banks, retail banks, financial planners and others'
#getPosTaggedData(text)


# In[5]:


def getEntitiesTagged(sent):
    posSent = ''
    doc = nlp(sent)
    posSent = "\t".join([token.text + '/' +token.label_+"/" + str(token.start_char) + "/" + str(token.end_char) for token in doc.ents])
    return posSent


# In[1]:


def getEntitiesTaggedAsList(sent):
    posSent = ''
    doc = nlp(sent)
    posSent = [(token.text, token.label_, str(token.start_char), str(token.end_char)) for token in doc.ents]
    return posSent


# #### This method will return entities, word, start pos, end pos

# In[6]:


#getEntitiesTagged('Apple is looking at buying U.K. startup for $1 billion')


# In[7]:


def getParseDataFromTextDict(sent):
    parsed_text_dict = {}
    doc = nlp(sent)
    #displacy.render(doc, style='dep', jupyter=True)
    for token in doc:
        parsed_text_dict[token.i] = ([token.text, token.dep_, token.head.text, token.head.i, token.head.pos_, [(child.text, child.i) for child in token.children]])
        #print(token)
    return parsed_text_dict


# In[39]:


def getParseDataFromText(sent):
    parsed_text_list = []
    doc = nlp(sent)
    #displacy.render(doc, style='dep', jupyter=True)
    for token in doc:
        parsed_text_list.append([token.text, token.dep_, token.head.text, token.head.pos_, [(child.text, child.i) for child in token.children]])
        #print(token)
    return parsed_text_list

#text = 'Wealth management is an investment-advisory discipline which incorporates financial planning, investment portfolio management and a number of aggregated financial services offered by a complex mix of asset managers, custodial banks, retail banks, financial planners and others'
#for line in getParseDataFromText(text):
#    print(line)
#visualizeParsedText(text)


# In[9]:


# sent = 'Apple is looking at buying U.K. startup for $1 billion'
# doc = nlp(sent)
# for token in doc:
#     parsed_text_list.append([token.text, token.dep_, token.head.text, token.head.i, token.head.pos_, [child.text for child in token.children]])
#     for child in token.children:
#         print(child, '\t', child.i, '\t')


# In[4]:


def visualizeParsedText(sent):
    doc = nlp(sent)
    displacy.render(doc, style='dep', jupyter=True)


# In[5]:


## Create verb to subject and object mapping
#visualizeParsedText('Apple is looking at buying U.K. startup for $1 billion')

# sentence = 'A private equity fund is a collective investment scheme used for making investments in various equity ( and to a lesser extent debt ) securities according to one of the investment strategies associated with private equity.'
# visualizeParsedText(sentence)

# print(getAllSubjectObjectRelation(getParseDataFromText(sentence), getPosTaggedData(sentence)))


# In[12]:


#visualizeParsedText('Mouse has been killed by the cat')
#visualizeParsedText('Cat killed the mouse')


# In[13]:


def getIndexParsedText(parsedDataFromSpacy, tokenTempIndex):
    for index in range(len(parsedDataFromSpacy)):
        if parsedDataFromSpacy[index][0] == tokenTempIndex:
            return index
        
    return -1


# In[32]:


def expandText(parsedDataFromSpacy, pos_data, token):
    #print(token)
    
    #print(pos_data)
    text = re.search('(([A-Za-z\\d\\.]+/(NOUN|PROPN) )+)?'+ token +'/[A-Za-z]+()?(([A-Za-z\\d\\.]+/(NOUN|PROPN) )+)?', pos_data).group()
    return " ".join([textSplit.split('/')[0] for textSplit in text.split(' ')])

def expandTextNew(parsedDataFromSpacy, tokenTempIndex):
    consider =['compound', 'quantmod', 'amod', 'npadvmod', 'det', 'conj']
    returnText = ''
    for index in range(0, len(parsedDataFromSpacy)):
        token       = parsedDataFromSpacy[index][0]
        rel         = parsedDataFromSpacy[index][1]
        head        = parsedDataFromSpacy[index][2]
        head_index  = parsedDataFromSpacy[index][3]
        head_pos    = parsedDataFromSpacy[index][4]
        childs      = parsedDataFromSpacy[index][5]
        if index == tokenTempIndex:
            indexList = []
            for child in childs:
                if parsedDataFromSpacy[child[1]][1] in consider:
                    indexList.append(child[1])
            indexList.append(tokenTempIndex)
            
            for index in range(min(indexList), max(indexList)+1):
                returnText += ' ' + parsedDataFromSpacy[index][0]
    return returnText.strip()
            #print(returnText.strip())

#text = 'Apple is looking at buying U.K. startup for $1 billion'
#text = 'This means that a legal mechanism is put into place which allows the lender to take possession and sell the secured property ("foreclosure" or "repossession") to pay off the loan in the event the borrower defaults on the loan or otherwise fails to abide by its terms.'
#expandTextNew(getParseDataFromTextDict(text), 21)


# ### Check for object presence on the basis of subject
#     * If subject is at left then object should be at right side of the verb
#     * Vice-versa

# In[33]:


# Find if currText is child of text
def isChildOf(parsedDataFromSpacy, currText, text, position):
    for parsedText in parsedDataFromSpacy:
        token = parsedText[0]
        dep = parsedText[1]
        head_text = parsedText[2]
        head_pos = parsedText[3]
        childs = parsedText[4]
        ## Immediate child
        if head_text == text:
            #print(currText, text)
            if currText in childs:
                return True
            
    return False 


# In[34]:


def getSubject(parsedDataFromSpacy, textIndex):
    for index in parsedDataFromSpacy.keys():
        parsedText      = parsedDataFromSpacy[index]
        token           = parsedText[0]
        dep             = parsedText[1]
        head_text       = parsedText[2]
        head_text_index = parsedText[3]
        head_pos        = parsedText[4]
        childs          = parsedText[5]
        
        if dep == 'nsubj' and head_text_index == textIndex:
            returnText = expandTextNew(parsedDataFromSpacy, index)
            return returnText
    return '' 


# In[35]:


def getObject(parsedDataFromSpacy, indexTemp):
    for index in range(0, len(parsedDataFromSpacy)):
        parsedText = parsedDataFromSpacy[index]
        token           = parsedText[0]
        dep             = parsedText[1]
        head_text       = parsedText[2]
        head_text_index = parsedText[3]
        head_pos        = parsedText[4]
        childs          = parsedText[5]
        #print(indexTemp, parsedDataFromSpacy[index])
        if dep in ['dobj', 'pobj'] and head_text_index == indexTemp:
            #print(parsedDataFromSpacy[index])
            returnText = expandTextNew(parsedDataFromSpacy, index)
            return returnText
    
    return ''


# In[36]:


def getAllSubjectObjectRelation(parsedDataFromSpacy):
    # list of tuple of type (subj, verb, obj)
    subj_obj_rel = []
    
    for index in range(0, len(parsedDataFromSpacy)):
        parsedText      = parsedDataFromSpacy[index]
        token           = parsedText[0]
        dep             = parsedText[1]
        head_text       = parsedText[2]
        head_text_index = parsedText[3]
        head_pos        = parsedText[4]
        childs          = parsedText[5]
        
        if head_pos=='VERB':
            #if head_text != 'incorporates':
            #    continue
            subject_ = getSubject(parsedDataFromSpacy, head_text_index)
            #print(subject_)
            object_ = getObject(parsedDataFromSpacy, head_text_index)
            subj_obj_rel.append((subject_, head_text, object_))
            #print((subject_, head_text, object_))
    return set(subj_obj_rel)

#parsedText = getParseDataFromTextDict('Apple is looking at buying U.K. startup for $1 billion')
#print(parsedText)
#parsedText = getParseDataFromTextDict('Dr Costanza Russo has developed a partnership with the Seven Pillars Institute for Global Finance and Ethics based in Kansas, and is working on a research project with Justice Blair and others on how to create an ethical culture in the banking sector.')
#parsedText = getParseDataFromTextDict('Mortgages can either be funded through the banking sector (that is, through short-term deposits) or through the capital markets through a process called "securitization", which converts pools of mortgages into fungible bonds that can be sold to investors in small denominations.')
#getAllSubjectObjectRelation(parsedText)
#getAllSubjectObjectRelation(getParseDataFromTextDict(text))


# In[16]:


# content = open('C:\\Saheb\\Projects\\Ontology creation\\Content downloaded from Internet\\Financial Law_html_0_cleaned.txt', encoding='utf8').read()

# for contentSplit in content.split('\n'):
#     for sentence in nltk.sent_tokenize(contentSplit):
#         print(sentence)
#         parsedText = getParseDataFromText(sentence)
#         #print(parsedText)
#         print(getAllSubjectObjectRelation(parsedText))
#         print('\n')


# In[17]:


# from subject_object_extraction import findSVOs

# # can still work even without punctuation
# for contentSplit in content.split('\n'):
#     for sentence in nltk.sent_tokenize(contentSplit):
#         print(sentence)
#         parse = nlp(sentence)
#         print(findSVOs(parse))
#         print()


# ### Using spacy vector similarity function

# In[18]:


def getSimilarity(word1, word2):
    tokens = nlp(word1+" "+word2)
    return tokens[0].similarity(tokens[1])


# ## Stanford CoreNLP

# In[1]:


from pycorenlp import StanfordCoreNLP
stanford_nlp = StanfordCoreNLP('http://localhost:9001')


# ### Pos tagging

# In[2]:


def getPOSTaggedDataFromTextUsingStanford(text):
    posSentences = []
    output = stanford_nlp.annotate(text, properties={'annotators': 'tokenize,ssplit,pos','outputFormat': 'json'})
    for s in output['sentences']:
        posSentences.append(" ".join([t["word"]+"/"+t["pos"] for t in s["tokens"]]))
    return posSentences


# ### Named entity tagging

# In[4]:


def getNERDataFromText(text):
    nerSentences = []
    output = stanford_nlp.annotate(text, properties={'annotators': 'tokenize, ssplit, pos, lemma,ner','outputFormat': 'json'})
    for s in output['sentences']:
        #print ("NER:\t", " ".join([t["word"]+"/"+t["ner"]+"/"+t["pos"] for t in s["tokens"]]))
        nerSentences.append(" ".join([t["word"]+"/"+t["ner"]+"/"+t["pos"] for t in s["tokens"]]))
    return nerSentences
#getNERDataFromText('Allegra Knopf Esq, Florida BarNo. 307660')


# ### Corenlp Coreference resolution

# In[21]:


#inputText= 'Messi was the first to win Euro cup. He is also the highest score of all time.'
def getCoreference(text):
    output = stanford_nlp.annotate(text, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, parse, dcoref','outputFormat': 'json'})
    #print(output['corefs'])
    sentList = []
    for sentenceJSONStr in output['sentences']:
        sentList.append(" ".join([t["word"] for t in sentenceJSONStr["tokens"]]))
    
    # Format will be sent Num/reference : sentNum/referenceTo
    reference_dict = {}
    for keyIterate in output['corefs'].keys():
        reference = ''
        referenceTo = ''
        if len(output['corefs'][keyIterate])>1:
            for jsonStr in output['corefs'][keyIterate]:
                if jsonStr['isRepresentativeMention'] == True:
                    reference = str(jsonStr['sentNum']) + "/" + jsonStr['text']
                elif jsonStr['isRepresentativeMention'] == False:
                    referenceTo = str(jsonStr['sentNum']) + "/" + jsonStr['text']
            reference_dict[reference] = referenceTo
    print(reference_dict)
    for reference in reference_dict.keys():
        referenceTo = reference_dict[reference].split("/")
        # -1 for sentence index
        sentList[int(referenceTo[0])-1] = sentList[int(referenceTo[0]) - 1].replace(referenceTo[1], reference.split("/")[1]) 
    return sentList

#getCoreference('MB Financial in Chicago is shutting down its national mortgage business.The $20 billion-asset company  that the decision was based on recent economic changes, heavy competition, “very low” margins and input from shareholders')


# In[22]:


#getSimilarity('mortgage_loan', 'home_loan')


# In[23]:


#getPOSTaggedDataFromTextUsingStanford('he difference between a mortgage banker and a  mortgage broker is that the mortgage banker funds loans with its own capital.')


# In[24]:


# text = 'Mortgage bank is a bank that specializes in originating and/or servicing mortgage loans.'
# output = stanford_nlp.annotate(text, properties={'annotators': 'tokenize, ssplit, pos, lemma, ner, parse, dcoref','outputFormat': 'json'})
# print(output['corefs'])
# sentList = []
# for sentenceJSONStr in output['sentences']:
#     sentList.append(" ".join([t["word"] for t in sentenceJSONStr["tokens"]]))

# # Format will be sent Num/reference : sentNum/referenceTo
# reference_dict = {}
# for keyIterate in output['corefs'].keys():
#     reference = ''
#     referenceTo = ''
#     if len(output['corefs'][keyIterate])>1:
#         for jsonStr in output['corefs'][keyIterate]:
#             if jsonStr['isRepresentativeMention'] == True:
#                 reference = str(jsonStr['sentNum']) + "/" + jsonStr['text']
#             elif jsonStr['isRepresentativeMention'] == False:
#                 referenceTo = str(jsonStr['sentNum']) + "/" + jsonStr['text']
#         reference_dict[reference] = referenceTo
# print(reference_dict)
# for reference in reference_dict.keys():
#     referenceTo = reference_dict[reference].split("/")
#     # -1 for sentence index
#     sentList[int(referenceTo[0])-1] = sentList[int(referenceTo[0]) - 1].replace(referenceTo[1], reference.split("/")[1]) 
# sentList


# ### Finding entity relations
# 
# #### Format for the returned object
#     * (Index, Token, POS, Relation (if any))
#     * Relation can be S -> subject, R -> Relation, O -> Object

# In[32]:


def getRelationBetweenEntitiesUsingStanford(sentence):
    sentenceRelation = []
    output = stanford_nlp.annotate(sentence, properties={"annotators":"tokenize,ssplit,pos,depparse,natlog,openie",
                                    "outputFormat": "json",
                                     "openie.triple.strict":"true",
                                     "openie.max_entailments_per_clause":"1"})
    for sentence in output['sentences']:
        print(sentence['openie'])
        for word in output['sentences'][0]['tokens']:
            isFound = False
            num=0
            for temp in sentence['openie']:
                num+=1
                if word['index'] > temp['subjectSpan'][0] and word['index'] <= temp['subjectSpan'][1]:
                    sentenceRelation.append((word['index'], word['originalText'], word['pos'], 'S' + str(num), ''))
                    isFound = True
                    break
                if word['index'] > temp['relationSpan'][0] and word['index'] <= temp['relationSpan'][1]:
                    sentenceRelation.append((word['index'], word['originalText'], word['pos'], 'R' + str(num), temp['relation']))
                    isFound = True
                    break
                if word['index'] > temp['objectSpan'][0] and word['index'] <= temp['objectSpan'][1]:
                    sentenceRelation.append((word['index'], word['originalText'], word['pos'], 'O' + str(num), ''))
                    isFound = True
                    break
            if not isFound:
                sentenceRelation.append((word['index'], word['originalText'], word['pos'], '', ''))
    return sentenceRelation


# In[33]:


def updateTuple(relationsTemp, tuple_to_update):
    relationsTempNew = []
    for index in range(0, len(relationsTemp)):
        relation = relationsTemp[index]
        if index in tuple_to_update.keys():
            relationsTempNew.append((relation[0], relation[1], relation[2], tuple_to_update[index], relation[4]))
        else:
            relationsTempNew.append(relation)
    return relationsTempNew


# In[34]:


def reviseSubjectObject(relations):
    tuple_to_update = {}
    for index in range(0, len(relations)):
        relation = relations[index]
        ## Checking Subject
        if relation[3] !='' and relation[3].startswith('S'):
            for index1 in reversed(range(0, index)):
                if relations[index1][2] in ['NN', 'NNS', 'NNP', 'JJ'] and relations[index1][3] != relation[3]:
                    tuple_to_update[index1] = relation[3]
                else:
                    break
                    
            for index1 in range(index+1, len(relations)):
                if relations[index1][2] in ['NN', 'NNS', 'NNP', 'JJ'] and relations[index1][3] != relation[3]:
                    tuple_to_update[index1] = relation[3]
                else:
                    break
        ## Checking Object
        elif relation[3] !='' and relation[3].startswith('O'):
            for index1 in reversed(range(0, index)):
                if relations[index1][2] in ['NN', 'NNS', 'NNP', 'JJ'] and relations[index1][3] != relation[3]:
                    tuple_to_update[index1] = relation[3]
                else:
                    break
                    
            for index1 in range(index+1, len(relations)):
                if relations[index1][2] in ['NN', 'NNS', 'NNP', 'JJ'] and relations[index1][3] != relation[3]:
                    tuple_to_update[index1] = relation[3]
                else:
                    break 
    relations_new = updateTuple(relations, tuple_to_update)
    return relations_new


# In[36]:


## testing relation finding
#sent = 'To prevent discrimination in the credit-granting process, the regulation imposes a delicate balance between the creditor’s need to know as much as possible about a prospective borrower with the borrower’s right not to disclose information irrelevant to the credit transaction as well as relevant information that is likely to be used in connection with discrimination on a prohibited basis. To this end, the regulation addresses taking, evaluating, and acting on applications as well as furnishing and maintaining credit information.'
#relations = getRelationBetweenEntitiesUsingStanford(sent)
#print(relations)
#reviseSubjectObject(relations)


# In[37]:


# subj_rel_obj_dict = {}

# for line in open('C:\Saheb\Projects\Ontology creation\Wikipedia documents\HTML_And_Cleaned_Text\\equity funds_cleaned.txt').read().split('\n'):
#     for sent in nltk.sent_tokenize(line):
#         rel_map = {}
#         relations = getRelationBetweenEntitiesUsingStanford(sent)
#         for relation in reviseSubjectObject(relations):
#             if relation[3]!='':    
#                 if relation[3] in rel_map:
#                     rel_map[relation[3]] = rel_map[relation[3]] + ' ' + relation[1]
#                 else:
#                     rel_map[relation[3]] = relation[1]
                    
#         for index in range(1, len(rel_map)):
#             S_index = 'S'+str(index)
#             O_index = 'O'+str(index)
#             R_index = 'R'+str(index)
#             if S_index in rel_map or O_index in rel_map or R_index in rel_map:
#                 S = ''
#                 R = ''
#                 O = ''
#                 if S_index in rel_map:
#                     S =rel_map[S_index]
#                 if R_index in rel_map:
#                     R =rel_map[R_index]
#                 if O_index in rel_map:
#                     O =rel_map[O_index]
                
#                 print((S, R, O))
#             else:
#                 break
                
#     print()


# #### End of enitty relation extraction 

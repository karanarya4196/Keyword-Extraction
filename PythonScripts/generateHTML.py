import re
import warnings
warnings.filterwarnings("ignore")

def highlightKeywordsInText(keywords_list, results, keyword_type, date_time, catId):
    for result in results:
        text = result['sectionText']
        document_name = re.sub(r'[^a-zA-Z0-9 \n\.]', '_', result['citation'])

        for keyword in keywords_list:
            text = text.replace(keyword, "<style> span {background-color: #ffff33;} </style> <span>" + keyword + '</span>')

        fw = open('../Output/CatId_{}_Keywords_'.format(catId) + date_time + '/' + keyword_type + '/{}.html'.format(document_name), 'w')
        for line in text.split('\n'):
            fw.write(line + '<br/>')
        fw.close()
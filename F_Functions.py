import sys
import requests
from PyPDF2 import PdfReader 
from bs4 import BeautifulSoup


def user_input_choose_from_list(options):
    number = 0
    for option in options:
        print(str(number) + " : " + option)
        sys.stdout.flush()
        number += 1

    user_choice = input("Which option is best to use?")
    return user_choice


def text_search(text_to_search,search_term):
    search_able = " ".join(text_to_search.split())

    start = 0
    end = len(search_able)

    snippets = []

    while start < end:
        first = search_able.find(search_term)
        if first == -1: start = end
        else: 
            snippets.append(search_able[start+len(search_term)-1:first])
            search_able = search_able[first+1:]

    return snippets


def DEFUNCT_get_510k_summary(Number):
    URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=' + Number
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find_all('table')
    #looks like the 7th table is the one I want
    rows = tables[7].find_all('tr')

    Summary = {}
    Summary['URL'] = URL
    for row in rows[1:]:
        try:
            header = row.find("th")
            data = row.find('td')
            Summary[header.text] = data.text.strip().replace("\n","").replace("\r","").replace('\xa0',"").replace('\t',"")
            if header.text == 'Summary': 
                link = row.find("a")
                Summary['Summary URL'] = link.get("href")
        except Exception as e:
            # print(e)
            continue    
        
    return Summary


def DEFUNCT_get_510k_pdf(Summary,output_folder='./output_folder/',silent=True):
    response = requests.get(Summary['Summary URL'])
    
    try:
        pdf = open(output_folder+str(Summary['510(k) Number'])+".pdf", 'wb')
        pdf.write(response.content)
        pdf.close()
        Summary['PDF Downloaded'] = "Yes"
        Summary['PDF Readable'] = "Unknown"
        Summary['PDF Location'] = output_folder+str(Summary['510(k) Number'])+".pdf"

        if not silent: print("File downloaded")
    except Exception as e:
        Summary['PDF Downloaded'] = "No"
        Summary['PDF Readable'] = "Unknown"
        Summary['PDF Location'] = "NA"
        if not silent: print(e)
    
    return Summary
    

def DEFUNCT_get_510k_IFU(Summary):
    # creating a pdf reader object 
    reader = PdfReader(Summary['PDF Location']) 
    
    # printing number of pages in pdf file 
    # print(len(reader.pages)) 
    
    # getting a specific page from the pdf file 
    page = reader.pages[1] 
    
    # extracting text from page 
    text = page.extract_text() 

    if text == "": 
        Summary['PDF Readable'] = "No"
        Summary['IFU'] = "Cannot Read PDF"

    else:
        all_text = ""
        for page in reader.pages:
            text = page.extract_text()
            all_text = all_text + text

        found_snippets = text_search(all_text,"Indications for Use")
        best_snippet = user_input_choose_from_list(found_snippets)
        selected_section = found_snippets[int(best_snippet)]
        Summary['IFU'] = text_search(selected_section,"Type of Use")[0]

    return Summary

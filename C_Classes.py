import sys
import requests
from PyPDF2 import PdfReader 
from bs4 import BeautifulSoup

from F_Functions import user_input_choose_from_list, text_search


class SUBMISSION:
    def __init__(self, number):
        self.Submission_Number = number
        self.Submission_Type = "Unknown"

    def summarize(self):
        attrs = vars(self)
        print(''.join("%s: %s \n" % item for item in attrs.items()))



class SUBMISSION_510K(SUBMISSION):
    def __init__(self, number):
        SUBMISSION.__init__(self, number)
        self.Submission_Type = "510K"

    def get_510k_summary(self):
        self.URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=' + self.Submission_Number
        page = requests.get(self.URL)

        soup = BeautifulSoup(page.content, "html.parser")
        tables = soup.find_all('table')
        #looks like the 7th table is the one I want
        rows = tables[7].find_all('tr')

        for row in rows[1:]:
            try:
                header = row.find("th")
                data = row.find('td')
                if header.text == "510(k) Number": pass
                else: self.__setattr__(header.text.replace(" ","_"),data.text.strip().replace("\n","").replace("\r","").replace('\xa0',"").replace('\t',""))
                if header.text == 'Summary': 
                    link = row.find("a")
                    self.Summary_URL = link.get("href")
            except Exception as e:
                # print(e)
                continue                
    
    def get_510k_pdf(self,output_folder='./output_folder/',silent=True):
        response = requests.get(self.Summary_URL)
        
        try:
            pdf = open(output_folder+str(self.Submission_Number)+".pdf", 'wb')
            pdf.write(response.content)
            pdf.close()
            self.PDF_Downloaded = "Yes"
            self.PDF_Readable = "Unknown"
            self.PDF_Location = output_folder+str(self.Submission_Number)+".pdf"

            if not silent: print("File downloaded")
        except Exception as e:
            self.PDF_Downloaded = "No"
            self.PDF_Readable = "Unknown"
            self.PDF_Location = "NA"
            if not silent: print(e)

    def get_510k_IFU(self):
        # creating a pdf reader object 
        reader = PdfReader(self.PDF_Location) 
                        
        # extracting text from page 
        page = reader.pages[1]
        text = page.extract_text() 

        if text == "": 
            self.PDF_Readable = "No"
            self.IFU = "Cannot Read PDF"

        else:
            self.PDF_Readable = "Yes"

            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text = all_text + text

            found_snippets = text_search(all_text,"Indications for Use")
            best_snippet = user_input_choose_from_list(found_snippets)
            selected_section = found_snippets[int(best_snippet)]
            self.IFU = text_search(selected_section,"Type of Use")[0]
            


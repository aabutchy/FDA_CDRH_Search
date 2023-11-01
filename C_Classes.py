import re
import sys
import requests
from PyPDF2 import PdfReader 
from bs4 import BeautifulSoup

from F_Functions import find_substring_in_string, clean_IFU, clean_end, clean_start, find_link

class SUBMISSION:
    def __init__(self, number):
        self.Submission_Number = number
        self.Submission_Type = "Unknown"

    def summarize(self):
        attrs = vars(self)
        print(''.join("%s: %s \n" % item for item in attrs.items()))

    def get_pdf(self,pdf_type,link,output_folder='./output_folder/',silent=True):
        response = requests.get(link)
        
        try:
            pdf = open(output_folder+str(self.Submission_Number)+"_"+str(pdf_type)+".pdf", 'wb')
            pdf.write(response.content)
            pdf.close()
            if not silent: print("File downloaded")
            return True

        except Exception as e:
            if not silent: print(e)
            return False
        
    def find_potential_predicates(self,filename):
        # creating a pdf reader object 
        reader = PdfReader(filename) 
                        
        # extracting text from page 
        page = reader.pages[1]
        text = page.extract_text() 

        if text == "":
            self.Potential_510k_Predicates = ['NA']
            self.Potential_De_Novo_Predicates = ['NA']
            self.Potential_Predicates = "Cannot Read PDF."

        else:
            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text = all_text + text

            found_510ks = re.findall('[K,k]\d{6}',all_text)
            found_De_Novos = re.findall('[D,d][E,e][N,n]\d{6}',all_text)

            found_510ks = list(set(found_510ks))
            found_De_Novos = list(set(found_De_Novos))
            if self.Submission_Number in found_510ks: found_510ks.remove(self.Submission_Number)
            if self.Submission_Number in found_De_Novos: found_De_Novos.remove(self.Submission_Number)

            self.Potential_510k_Predicates = found_510ks
            self.Potential_De_Novo_Predicates = found_De_Novos
            self.Potential_Predicates = found_510ks + found_De_Novos


class SUBMISSION_510K(SUBMISSION):
    def __init__(self, number):
        SUBMISSION.__init__(self, number)
        self.Submission_Type = "510K"
        if not re.match('[K,k]\d{6}', number): print("This does not look like a 510k Submission number!")

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
                else:
                    try:
                        self.__setattr__(header.text.replace(" ","_"),data.text.strip().replace("\n","").replace("\r","").replace('\xa0',"").replace('\t',""))
                        found, url = find_link(row,header)
                        if found: 
                            if url[0] == "/": url = 'https://www.accessdata.fda.gov' + url
                            self.__setattr__(str(header.text.replace(" ","_"))+"_URL",url)
                    except Exception as e:
                        # print('ERROR ')
                        # print(e)
                        continue
            except Exception as e:
                # print(e)
                continue                
           
    def get_510k_pdf(self,output_folder='./output_folder/',silent=True):
        success = self.get_pdf("Summary",self.Summary_URL,output_folder=output_folder,silent=silent)

        if success:
            self.PDF_Downloaded = "Yes"
            self.PDF_Readable = "Unknown"
            self.PDF_Location = output_folder+str(self.Submission_Number)+"_Summary.pdf"
        else:
            self.PDF_Downloaded = "No"
            self.PDF_Readable = "Unknown"
            self.PDF_Location = "NA"

    def get_510k_IFU(self):
        # creating a pdf reader object 
        reader = PdfReader(self.PDF_Location) 
                        
        # extracting text from page 
        page = reader.pages[1]
        text = page.extract_text() 

        if text == "": 
            self.PDF_Readable = "No"
            self.IFU = "Cannot Read PDF."

        else:
            self.PDF_Readable = "Yes"

            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text = all_text + text

            found, found_snippets = find_substring_in_string("Indications for Use", all_text)
            # print(found_snippets)
            if found:
                for snippet in found_snippets:
                    found, IFU = find_substring_in_string("Type of Use", snippet)
                    if found: 
                        temp1 = clean_IFU(IFU[0],'Indications for Use',"")
                        temp2 = clean_end(temp1)
                        temp3 = clean_start(temp2)
                        self.IFU = temp3
            else: 
                self.IFU = "Not Automatically Found."
    

class SUBMISSION_DE_NOVO(SUBMISSION):
    def __init__(self, number):
        SUBMISSION.__init__(self, number)
        self.Submission_Type = "De Novo 510(k)"
        if not re.match('[D,d][E,e][N,n]\d{6}', number): print("This does not look like a De Novo Submission number!")

    def get_De_Novo_summary(self):
        self.URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?id=' + self.Submission_Number
        page = requests.get(self.URL)

        soup = BeautifulSoup(page.content, "html.parser")
        tables = soup.find_all('table')
        #looks like the 7th table is the one I want
        rows = tables[7].find_all('tr')

        for row in rows[1:]:
            try:
                header = row.find("th")
                data = row.find('td')
                try:
                    self.__setattr__(header.text.replace(" ","_"),data.text.strip().replace("\n","").replace("\r","").replace('\xa0',"").replace('\t',""))
                    found, url = find_link(row,header)
                    if found: 
                        if url[0] == "/": url = 'https://www.accessdata.fda.gov' + url
                        self.__setattr__(str(header.text.replace(" ","_"))+"_URL",url)
                except Exception as e:
                    # print('ERROR ')
                    # print(e)
                    continue
            except Exception as e:
                # print(e)
                continue                

    def get_Reclassification_pdf(self,output_folder='./output_folder/',silent=True):
        success = self.get_pdf("Reclassification",self.Reclassification_Order_URL,output_folder=output_folder,silent=silent)

        if success:
            self.PDF_Reclassification_Downloaded = "Yes"
            self.PDF_Reclassification_Readable = "Unknown"
            self.PDF_Reclassification_Location = output_folder+str(self.Submission_Number)+"_Reclassification.pdf"
        else:
            self.PDF_Reclassification_Downloaded = "No"
            self.PDF_Reclassification_Readable = "Unknown"
            self.PDF_Reclassification_Location = "NA"

    def get_FDA_Review_pdf(self,output_folder='./output_folder/',silent=True):
        success = self.get_pdf("Review",self.FDA_Review_URL,output_folder=output_folder,silent=silent)

        if success:
            self.PDF_Review_Downloaded = "Yes"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = output_folder+str(self.Submission_Number)+"_Review.pdf"
        else:
            self.PDF_Review_Downloaded = "No"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = "NA"

    def get_De_Novo_IFU(self):
        # creating a pdf reader object 
        reader = PdfReader(self.PDF_Review_Location) 
                        
        # extracting text from page 
        page = reader.pages[1]
        text = page.extract_text() 

        if text == "": 
            self.PDF_Review_Readable = "No"
            self.IFU = "Cannot Read PDF"

        else:
            self.PDF_Review_Readable = "Yes"

            all_text = ""
            for page in reader.pages:
                text = page.extract_text()
                all_text = all_text + text

            found, found_snippets = find_substring_in_string("INDICATIONS FOR USE", all_text)
            if found:
                for snippet in found_snippets:
                    found, IFU = find_substring_in_string("IMITATIONS", snippet)
                    if found: 
                        temp1 = clean_IFU(IFU[0],'INDICATIONS FOR USE',"")
                        temp2 = clean_end(temp1)
                        temp3 = clean_start(temp2)
                        self.IFU = temp3
                        break
            else: 
                self.IFU = "Not Automatically Found."


class SUBMISSION_PMA(SUBMISSION):
    def __init__(self, number):
        SUBMISSION.__init__(self, number)
        self.Submission_Type = "PMA"
        if not re.match('[P,p]\d{6}', number): print("This does not look like a PMA Submission number!")

    def get_PMA_summary(self):
        self.URL = 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id=' + self.Submission_Number
        page = requests.get(self.URL)

        soup = BeautifulSoup(page.content, "html.parser")
        tables = soup.find_all('table')
        #looks like the 7th table is the one I want
        rows = tables[7].find_all('tr')

        for row in rows[1:]:
            if 'Approval Order Statement' in row.text:
                temp = str(row)
                starter = temp.find('<br/>')
                description = temp[starter+5:]
                description = clean_end(description)
                self.Approval_Order_Statement = description
            try:
                header = row.find("th")
                data = row.find('td')
                if not header.text == "Supplements:":
                    try:
                        self.__setattr__(header.text.replace(" ","_"),data.text.strip().replace("\n","").replace("\r","").replace('\xa0',"").replace('\t',""))
                        found, url = find_link(row,header)
                        if found: 
                            if url[0] == "/": url = 'https://www.accessdata.fda.gov' + url
                            self.__setattr__(str(header.text.replace(" ","_"))+"_URL",url)
                    except Exception as e:
                        # print('ERROR ')
                        # print(e)
                        continue
            except Exception as e:
                # print(e)
                continue                

    def get_FDA_Approval_Order_pdf(self,output_folder='./output_folder/',silent=True):
        success = self.get_pdf("Approval_Order",self.Approval_Order_URL,output_folder=output_folder,silent=silent)

        if success:
            self.PDF_Review_Downloaded = "Yes"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = output_folder+str(self.Submission_Number)+"_Approval_Order.pdf"
        else:
            self.PDF_Review_Downloaded = "No"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = "NA"

    def get_FDA_Summary_pdf(self,output_folder='./output_folder/',silent=True):
        success = self.get_pdf("Summary",self.Summary_URL,output_folder=output_folder,silent=silent)

        if success:
            self.PDF_Review_Downloaded = "Yes"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = output_folder+str(self.Submission_Number)+"_Summary.pdf"
        else:
            self.PDF_Review_Downloaded = "No"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = "NA"

    def get_FDA_Labeling_pdf(self,output_folder='./output_folder/',silent=True):
        success = self.get_pdf("Labeling",self.Labeling_URL,output_folder=output_folder,silent=silent)

        if success:
            self.PDF_Review_Downloaded = "Yes"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = output_folder+str(self.Submission_Number)+"_Labeling.pdf"
        else:
            self.PDF_Review_Downloaded = "No"
            self.PDF_Review_Readable = "Unknown"
            self.PDF_Review_Location = "NA"


# Approval_Order_URL: https://www.accessdata.fda.gov/cdrh_docs/pdf22/P220005A.pdf 
# Summary: Summary of Safety and Effectiveness 
# Summary_URL: https://www.accessdata.fda.gov/cdrh_docs/pdf22/P220005B.pdf 
# Labeling: Labeling 
# Labeling_URL: https://www.accessdata.fda.gov/cdrh_docs/pdf22/P220005C.pdf 

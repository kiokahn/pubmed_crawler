"""
#### PubMedFetcher Defination ####
https://pypi.org/project/metapub/

fetch = PubMedFetcher()
article = fetch.article_by_pmid('123456')
print(article.title)
print(article.journal, article.year, article.volume, article.issue)
print(article.authors)
print(article.citation)
"""

import sys
from metapub import PubMedFetcher


class PubMedCrawl:

    def __init__(self, keyword, retmax, checkBox):
        self.keyword = keyword
        self.retmax = retmax
        self.checkBox = checkBox
        self.chem_json_list = []
        self.chem_list = []
        self.name_dict = []
        self.title_list = []
        
        #added by kiokahn - start
        self.journal_list = []
        self.year_list = []
        self.volume_list = []
        self.issue_list = []
        self.authors_list = []
        self.citation_list = []
        #added by kiokahn - end
        
        self.abstract_list = []
        self.chem_matrix = []
        self.count = 5

    def run(self):
        if not self.checkBox:
            try:
                self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(self.keyword)
            except TimeoutError:
                #self.textBrowser_value.emit("Please Check Internet Connection! Retrying!")
                print("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict = self.process_pubmed_chem_info(self.keyword)
        else:
            '''
            try:
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(self.keyword)
            except TimeoutError:
                #self.textBrowser_value.emit("Please Check Internet Connection! Retrying!")
                print("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(self.keyword)
            '''
            try:
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, \
                    self.journal_list, self.year_list, self.volume_list, self.issue_list, self.authors_list, self.citation_list,\
                        self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(self.keyword)
            except TimeoutError:
                #self.textBrowser_value.emit("Please Check Internet Connection! Retrying!")
                print("Please Check Internet Connection! Retrying!")
                self.chem_json_list, self.chem_list, self.name_dict, self.title_list, \
                   self.journal_list, self.year_list, self.volume_list, self.issue_list, self.authors_list, self.citation_list, \
                       self.abstract_list = \
                    self.process_pubmed_chem_abstract_info(self.keyword)
            
        if self.chem_json_list:
            self.chem_matrix = self.process_matrix()
            self.make_csv_single_chem()
        else:
            #self.textBrowser_value.emit("No Result Found!")
            print("No Result Found!")


    def crawl_chem_json(self, keyword, retmax=2000):#300):
        fetch = PubMedFetcher()

        pmids = fetch.pmids_for_query(keyword, retmax=retmax)

        #self.textBrowser_value.emit("Scanning Iteration : " + str(retmax))
        print("Scanning Iteration : " + str(retmax))
        self.textBrowser_value.emit("Expected Running Time : " + str(retmax * 2) + " seconds.")
        print("Expected Running Time : " + str(retmax * 2) + " seconds.")

        #self.textBrowser_value.emit("PMID Scan Done!")
        print("PMID Scan Done!")
        #self.progress_bar_value.emit(self.count)
        print(self.count)

        json_dicts = []
        #self.textBrowser_value.emit("Crawling Paper Info..")
        print("Crawling Paper Info..")

        for i in range(len(pmids)):
            pmid = pmids[i]
            try:
                if int(i / len(pmids) * 100) > self.count:
                    self.count = int(i / len(pmids) * 100)
                    #self.progress_bar_value.emit(self.count)
                    print(self.count)
                try:
                    article = fetch.article_by_pmid(pmid)
                except:
                    #self.textBrowser_value.emit("Error reading " + str(pmid))
                    print("Error reading " + str(pmid))
                    continue

                chemical = article.chemicals
                if not chemical:
                    continue

                json_dicts.append(chemical)
            except:
                continue

        #self.textBrowser_value.emit("Progress Done!")
        print("Progress Done!")
        return json_dicts

    def make_csv_single_chem(self, outfile=None):
        if not outfile:
            if self.checkBox:
                outfile = "../[with_abstract] " + self.keyword + ".csv"
            else:
                outfile = "../[frequency] " + self.keyword + ".csv"
        header = ["Compound ID", "Name", "Frequency"]

        if self.checkBox:
            header.append("Title")

            #added by kiokahn - start
            header.append("Journal")
            header.append("Year")
            header.append("Volume")
            header.append("Issue")
            header.append("Authors")
            header.append("Citation")
            #added by kiokahn - end

            header.append("Abstract")

        ofile = open(outfile, 'w', encoding="utf8")
        ofile.write(", ".join(header))

        for i in range(len(self.chem_list)):
            compound_id = self.chem_list[i]
            name = self.name_dict[compound_id].replace(",", "*")
            frequency = str(self.chem_matrix[i][i])
            contents = [compound_id, name, frequency]
            if self.checkBox:
                title = self.title_list[i]
                
                #added by kiokahn - start
                journal = self.journal_list[i]
                year = self.year_list[i]
                volume = self.volume_list[i]
                issue = self.issue_list[i]
                authors = self.authors_list[i]
                citation = self.citation_list[i]
                #added by kiokahn - end
                
                abstract = self.abstract_list[i]
                contents.append(title)
                
                #added by kiokahn - start
                contents.append(journal)
                contents.append(year)
                contents.append(volume)
                contents.append(issue)
                contents.append(authors)
                contents.append(citation)
                #added by kiokahn - end
                
                contents.append(abstract)

            ofile.write("\n" + ", ".join(contents))

        ofile.close()

        #self.textBrowser_value.emit("Result Saved as a CSV File")
        print("Result Saved as a CSV File")
        #self.textBrowser_value.emit("Filename : " + outfile)
        print("Filename : " + outfile)
        #self.progress_bar_value.emit(100)
        print(100)

    def process_matrix(self):
        num_chem = len(self.chem_list)
        matrix = [[0 for i in range(num_chem)] for j in range(num_chem)]

        for chem_json in self.chem_json_list:
            keys = list(chem_json.keys())

            IDXs = []

            for el in keys:
                #added by kiokahn - start
                #if el in "title abstract":
                if el in "title journal year volume issue authors citation abstract":
                    #added by kiokahn - end
                    continue
                idx = self.chem_list.index(el)
                matrix[idx][idx] += 1
                IDXs.append(idx)

        return matrix

    def process_pubmed_chem_info(self, keyword):
        chem_json_list = self.crawl_chem_json(keyword, retmax=self.retmax)
        #self.textBrowser_value.emit("Crawling Done! Processing Output Files...")
        print("Crawling Done! Processing Output Files...")
        chem_list = []
        name_dict = {}

        for chem_json in chem_json_list:
            for chem in chem_json.keys():
                if chem not in chem_list:
                    chem_list.append(chem)
                    name_dict[chem] = chem_json[chem]["substance_name"]

        #self.textBrowser_value.emit("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        print("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        #self.textBrowser_value.emit("Total Number of Chemicals : " + str(len(chem_list)))
        print("Total Number of Chemicals : " + str(len(chem_list)))

        return chem_json_list, chem_list, name_dict

    def process_pubmed_chem_abstract_info(self, keyword):
        chem_json_list = self.crawl_chem_abstract(keyword, retmax=self.retmax)
        #self.textBrowser_value.emit("Crawling Done! Processing Output Files...")
        chem_list = []
        title_list = []
        
        #added by kiokahn - start
        journal_list = []
        year_list = []
        volume_list = []
        issue_list = []
        authors_list = []
        citation_list = []
        #added by kiokahn - end
        
        abstract_list = []
        name_dict = {}

        for chem_json in chem_json_list:
            for key in chem_json.keys():
                #added by kiokahn - start
                #if key in "title abstract":
                if key in "title journal year volume issue authors citation abstract":
                    #added by kiokahn - end
                    continue

                if key not in chem_list:
                    chem_list.append(key)
                    title_list.append(chem_json["title"])
                    
                    #added by kiokahn - start
                    journal_list.append(chem_json["journal"])
                    year_list.append(chem_json["year"])
                    volume_list.append(chem_json["volume"])
                    issue_list.append(chem_json["issue"])
                    authors_list.append(chem_json["authors"])
                    citation_list.append(chem_json["citation"])
                    #added by kiokahn - end

                    abstract_list.append(chem_json["abstract"])
                    name_dict[key] = chem_json[key]["substance_name"]

        #self.textBrowser_value.emit("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        print("Total Number of Crawled Papers : " + str(len(chem_json_list)))
        #self.textBrowser_value.emit("Total Number of Chemicals : " + str(len(chem_list)))
        print("Total Number of Chemicals : " + str(len(chem_list)))
        
        '''
        return chem_json_list, chem_list, name_dict, title_list, abstract_list
        '''
        #added by kiokahn - start
        return chem_json_list, chem_list, name_dict, title_list, \
            journal_list, year_list, volume_list, issue_list, authors_list, citation_list,\
                abstract_list
        #added by kiokahn - end

    def crawl_chem_abstract(self, keyword, retmax=2000):
        fetch = PubMedFetcher()
        #self.progress_bar_value.emit(self.count)

        pmids = fetch.pmids_for_query(keyword, retmax=retmax)

        #self.textBrowser_value.emit("Scanning Iteration : " + str(retmax))
        #self.textBrowser_value.emit("Expected Running Time : " + str(retmax * 2) + " seconds.")

        #self.textBrowser_value.emit("PMID Scan Done!")

        json_dicts = []
        #self.textBrowser_value.emit("Crawling Paper Info..")

        for i in range(len(pmids)):
            pmid = pmids[i]
            try:
                if int(i / len(pmids) * 100) > self.count:
                    self.count = int(i / len(pmids) * 100)
                    #self.progress_bar_value.emit(self.count)
                    print(self.count)

                try:
                    article = fetch.article_by_pmid(pmid)
                except:
                    #self.textBrowser_value.emit("Error reading " + str(pmid))
                    print("Error reading " + str(pmid))
                    continue

                chemical = article.chemicals
                if not chemical:
                    continue

                abstract = article.abstract.replace(",", "*")
                if not abstract:
                    continue
                elif "\t" in abstract or "\n" in abstract:
                    abstract = abstract.replace("\t", " ")
                    abstract = abstract.replace("\n", " ")

                title = article.title
                if not title:
                    continue
                elif "\t" in title or "\n" in title:
                    title = title.replace("\t", " ")
                    title = title.replace("\n", " ")
                    
                #added by kiokahn - start
                journal = article.journal
                if not journal:
                    continue
                elif "\t" in journal or "\n" in journal:
                    journal = journal.replace("\t", " ")
                    journal = journal.replace("\n", " ")
                    
                year = article.year
                if not year:
                    continue
                elif "\t" in year or "\n" in year:
                    year = year.replace("\t", " ")
                    year = year.replace("\n", " ")

                volume = article.volume
                if not volume:
                    continue
                elif "\t" in volume or "\n" in volume:
                    volume = volume.replace("\t", " ")
                    volume = volume.replace("\n", " ")

                issue = article.issue
                if not issue:
                    continue
                elif "\t" in issue or "\n" in issue:
                    issue = issue.replace("\t", " ")
                    issue = issue.replace("\n", " ")

                authors = article.authors_str
                if not authors:
                    continue
                elif "\t" in authors or "\n" in authors:
                    authors = authors.replace("\t", " ")
                    authors = authors.replace("\n", " ")

                citation = article.citation
                if not citation:
                    continue
                elif "\t" in citation or "\n" in citation:
                    citation = citation.replace("\t", " ")
                    citation = citation.replace("\n", " ")
                #added by kiokahn - end
                    

                chemical["title"] = title
                
                #added by kiokahn - start
                chemical["journal"] = journal
                chemical["year"] = year
                chemical["volume"] = volume
                chemical["issue"] = issue
                chemical["authors"] = authors
                chemical["citation"] = citation
                #added by kiokahn - end
                
                chemical["abstract"] = abstract

                json_dicts.append(chemical)
            except:
                continue

        #self.textBrowser_value.emit("Progress Done!")
        print("Progress Done!")
        return json_dicts


if __name__ == "__main__":
    retmax = 3000
    crawl = PubMedCrawl('Germ cell', retmax, True)
    crawl.run()
    
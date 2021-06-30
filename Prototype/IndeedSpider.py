from fake_useragent import UserAgent
from urllib import request
import re
import time,random
import datetime
import csv

class IndeedSpider(object):
    def __init__(self):
        self.url = 'https://ca.indeed.com/jobs?q={}&l={}&jt={}&fromage={}&start={}'
        self.index = 0

    def get_header(self):
        ua = UserAgent(use_cache_server=False)
        headers = {'User-Agent': random.choice(ua.random)}
        return headers

    def get_html(self,url):
        headers = self.get_header()
        req = request.Request(url=url,headers=headers)
        res = request.urlopen(req)
        html = res.read().decode()
        # print(html)
        # Retrieving and pass to parse function
        self.parse_html(html)

    def parse_html(self,html):
        #[(url,title,company,location),(url,title....]
        re_pattern = '<h2 class="title">.*?<a.*?target="_blank".*?href="(.*?)".*?title="(.*?)".*?<span class="company">(.*?)</span>.*?"location accessible-contrast-color-location">(.*?)<'
        pattern = re.compile(re_pattern,re.S)
        r_list = pattern.findall(html)

        # Parsed and pass to saving function
        self.write_html(r_list)

    def write_html(self,r_list):
        # List to store all job info
        L = []
        # Item to store a job info
        item = {}
        with open('jobs.csv','a') as f:
            writer = csv.writer(f)
            for r in r_list:
                item['JobTitle'] = self.__replaceAll__(r[1].strip())

                # check if there's hyperlink attached to 'company' HTML
                company_name = r[2].strip()
                new_company_name = self.__parse_string__(company_name)
                item['Company'] = self.__replaceAll__(new_company_name)

                # get current time
                date = datetime.datetime.now()
                # put date in format: MON-DD
                item['Date'] = date.strftime("%b") + '-' + date.strftime("%d")
                item['Location'] = r[3].strip()
                item['URL'] = "https://ca.indeed.com" + r[0].strip()
                # print(item)

                t = ('',item['Company'],item['JobTitle'],item['Date'],item['Location'],'',item['URL'])
                # append each tuple of job info to List
                L.append(t)
                self.index += 1

            # write and save in excel
            writer.writerows(L)

    def run(self):
        jobTitle = str(input('Jobtitle(replace space with +):'))
        location = str(input('Location(City/dont specify):'))
        numofPages = int(input('Number of pages you want to search(Integer):'))
        numofPages = numofPages*10-10
        jobType = str(input('Enter jobtype(Fulltime/Parttime/Permanent/Contract/Temporary/dont specify):'))
        datePosted = input('PastDays(1/3/7/14/dont specify):')
        for offset in range(0,numofPages+1,10):
            url = self.url.format(jobTitle,location,jobType,datePosted,offset)
            #print(url)
            self.get_html(url)
            time.sleep(random.uniform(1,2))  #randomly generate float sleep time to
        print("numberofJobs: %d" % self.index)

    # Helper function to remove all HTML with blank
    def __replaceAll__(self,str):
        if str.__contains__('<b>') or str.__contains__('</b>') or str.__contains__('‚Äì') or str.__contains__('&amp;'):
            str = str.replace('<b>','')
            str = str.replace('</b>','')
            str = str.replace('‚Äì', '-')
            str = str.replace('&amp;','&')
        # print(str)
        return str

    # Helper function to remove TARGET: item['Company'] irregular HTML where len(str)>40
    def __parse_string__(self,str):
        if len(str) >= 50:
            str_list = str.partition('>')
            if str_list[2].__contains__('</a>'):
                return str_list[2][:-4]
            return str_list[2]
        else:
            return str


if __name__ =='__main__':
    start = time.time()
    indeedSpider = IndeedSpider()
    indeedSpider.run()
    end = time.time()
    print('used time: %.2f'%(end-start))

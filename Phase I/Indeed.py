from fake_useragent import UserAgent
from urllib import request
import re
import time,random
import datetime
import csv
from lxml import etree

class IndeedSpider(object):
    def __init__(self):
        self.url = 'https://ca.indeed.com/jobs?q={}&l={}&jt={}&fromage={}&start={}'
        self.index = 0
        # self.keyword = ''

    def get_header(self):
        ua = UserAgent()
        headers = {'User-Agent': random.choice(ua.random)}
        return headers

    def get_html(self,url):
        headers = self.get_header()
        req = request.Request(url=url,headers=headers)
        res = request.urlopen(req)
        html = res.read().decode()
        # print(html)
        return html

    def parse_html(self,html,re_pattern):

        pattern = re.compile(re_pattern,re.S)
        r_list = pattern.findall(html)

        # Parsed and pass to saving function
        return r_list

    def write_html(self,r_list):
        # List to store all job info
        L = []
        # Item to store a job info
        item = {}
        with open('jobs.csv','a') as f:
            writer = csv.writer(f)
            for r in r_list:


                item['JobTitle'] = self.__clean_html__(r[1].strip())

                # check if there's hyperlink attached to 'company' HTML
                company_name = self.__parse_string__(r[2].strip())
                item['Company'] = self.__clean_html__(company_name)

                # get current time
                date = datetime.datetime.now()
                # put date in format: MON-DD
                item['Date'] = date.strftime("%b") + '-' + date.strftime("%d")
                item['Location'] = self.__clean_html__(r[3].strip())

                # url_strip = self.__get_urlStrip__(r[0])
                # inner_url = "https://ca.indeed.com/viewjob" + url_strip[0] + "&from=serp&vjs=3"
                inner_url = "https://ca.indeed.com" + r[0].strip()
                # print('INNER URL:' + inner_url)

                inner_html = self.get_html(inner_url)
                # print(inner_html)

                website_url = self.__parse_inner_url__(inner_html)
                if (len(website_url) == 0):
                    item['URL'] = inner_url
                else:
                    item['URL'] = website_url[0].strip()

                # Still NOT SURE WHAT TO DO WITH THE DESCRIPTION PART YET, WAIT AND SEE
                inner_desc = self.__parse_description__(inner_html)
                item['description'] = inner_desc

                # print(item)

                t = ('',item['Company'],item['JobTitle'],item['Date'],item['Location'],'',item['description'],item['URL'])
                # append each tuple of job info to List
                L.append(t)
                self.index += 1

            # write and save in excel
            writer.writerows(L)

    # get the description of job from the inner url webpage
    def __parse_description__(self, html):
        # [(description)] format with all HTML that needs to be cleaned
        xpath_pattern = '//div[@id="jobDescriptionText"]/div/p | //div[@id="jobDescriptionText"]/div/ul | //div[@id="jobDescriptionText"]/p | //div[@id="jobDescriptionText"]/ul | //div[@id="jobDescriptionText"]/div/div | //div[@id="jobDescriptionText"] | //div[@id="jobDescriptionText"]/div'
        # xpath_pattern = '//div[@id="jobDescriptionText"]'
        parse_html = etree.HTML(html)
        inner_desc_list = parse_html.xpath(xpath_pattern)
        description = []
        for desc in inner_desc_list:
            description += desc.xpath('.//text()')
        # print(description)

        return description

    # get the website url of the job from the inner url webpage
    def __parse_inner_url__(self, html):
        xpath_pattern = '//div[@class="icl-u-lg-hide"]/a/@href'
        parse_html = etree.HTML(html)
        inner_url_list = parse_html.xpath(xpath_pattern)
        # print(inner_url_list)
        return inner_url_list

    def run(self):
        jobTitle = str(input('Jobtitle(replace space with +):'))
        location = str(input('Location(City/dont specify):'))
        numofPages = int(input('Number of pages you want to search(Integer):'))
        numofPages = numofPages*10-10
        jobType = str(input('Enter jobtype(Fulltime/Parttime/Permanent/Contract/Temporary/dont specify):'))
        datePosted = input('PastDays(1/3/7/14/dont specify):')
        # Criteria = str(input('Please enter a key word or phrase to exclude irrelevant jobs:'))
        # self.keyword = Criteria
        pageNumber = 1
        for offset in range(0,numofPages+1,10):
            url = self.url.format(jobTitle,location,jobType,datePosted,offset)
            #print(url)
            html = self.get_html(url)

            # [(url,title,company,location),(url,title....]
            re_pattern = '<h2 class="title">.*?<a.*?target="_blank".*?href="(.*?)".*?title="(.*?)".*?<span class="company">(.*?)</span>.*?"location accessible-contrast-color-location">(.*?)<'
            r_list = self.parse_html(html,re_pattern)
            self.write_html(r_list)
            # randomly generate float sleep time for each request
            time.sleep(random.uniform(1,2))

            print("Finish page " + str(pageNumber) + " on indeed")
            pageNumber += 1

        print("numberofJobs: %d" % self.index)

    # Helper function to remove all HTML with blank
    def __clean_html__(self,str):
        if str.__contains__('<b>') or str.__contains__('</b>') or str.__contains__('‚Äì') or str.__contains__('&amp;') or str.__contains__('√©'):
            str = str.replace('<b>','')
            str = str.replace('</b>','')
            str = str.replace('‚Äì', '-')
            str = str.replace('&amp;','&')
            str = str.replace('√©','é')
        # print(str)
        return str


    # get the segment of the URL that is required to open inner html
    def __get_urlStrip__(self,url):
        re_pattern = '/rc/clk?(.*?)&fccid'
        pattern = re.compile(re_pattern, re.S)
        r_list = pattern.findall(url)
        return r_list

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

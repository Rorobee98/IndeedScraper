from fake_useragent import UserAgent
from urllib import request
import re
import time, random
import datetime
import csv
import requests
from lxml import etree


class IndeedSpider(object):
    def __init__(self):
        self.url = 'https://ca.indeed.com/jobs?'
        self.index = 0

    def get_header(self):
        ua = UserAgent()
        headers = {'User-Agent':random.choice(ua.random)}
        # print(headers.keys(),headers.values())
        return headers

    def get_html(self, url, params={}):
        headers = self.get_header()
        res = requests.get(url=url, params=params, headers=headers)
        html = res.content
        # Retrieving and pass to parse function
        # DEBUG 1
        # print(html.decode())
        self.parse_html(html.decode())

    def parse_html(self, html):
        # Previous version Failed now - Feb 24 2022
        # [(url,title,company,location),(url,title....]
        # re_pattern = 'class="tapItem fs-unmask result.*?href="(.*?)".*?<td class="resultContent">.*?<span title="(.*?)">.*?<span class="company">(.*?)</span>.*?<div class="CompanyLocation">(.*?)<'

        # New Version - Feb 24 2022
        # Get URl
        url_pattern = 'class="tapItem fs-unmask result.*?href="(.*?)"'
        pattern = re.compile(url_pattern, re.S)
        url_list = pattern.findall(html)
        # DEBUG URL
        parse_html = etree.HTML(html)
        # print(url_list)
        #GET Jobtitle List
        job_pattern = '//*/div[1]/div/div[1]/div/table[1]/tbody/tr/td/div[1]/h2/span'
        jobtitle_list = parse_html.xpath(job_pattern)
        # GET Company Name list
        company_pattern = '//span[@class="companyName"]'
        company_list = parse_html.xpath(company_pattern)
        # GET Location List
        location_pattern = '//div[@class="companyLocation"]'
        location_list = parse_html.xpath(location_pattern)
        # put all list into one for loop using zip
        zip_job_list = zip(jobtitle_list,company_list,location_list,url_list)
        list = []
        # put new list in this order[(title,company,location,url),(title,company....]
        for job,company,location,url in zip_job_list:
            row = (job.xpath('.//text()'), company.xpath('.//text()'), location.xpath('.//text()'),url)
            # print(row)
            list.append(row)

        # send it to write_html for data output in Excel format
        self.write_html(list)

    def write_html(self, list):
        # List to store all job info
        L = []
        # Item to store a job info
        item = {}
        with open('jobs.csv', 'a') as f:
            writer = csv.writer(f)
            # [(title, company, location, url), (title, company....]
            for r in list:
                item['JobTitle'] = r[0][0]
                item['Company'] = r[1][0]
                # get current time
                date = datetime.datetime.now()
                # put date in format: MON-DD
                item['Date'] = date.strftime("%b") + '-' + date.strftime("%d")
                item['Location'] = r[2][0]
                item['URL'] = "https://ca.indeed.com" + r[3]
                # print(item)
                t = ('', item['Company'], item['JobTitle'], item['Date'], item['Location'], '', item['URL'])
                # append each tuple of job info to List
                L.append(t)
                self.index += 1

            # write and save in excel
            writer.writerows(L)

    def run(self):
        jobTitle = str(input('Jobtitle(replace space with +):'))
        location = str(input('Location(City/dont specify):'))
        numofPages = int(input('Number of pages you want to search(Integer):'))
        numofPages = numofPages * 10 - 10
        jobType = str(input('Enter jobtype(Fulltime/Parttime/Permanent/Contract/Temporary/dont specify):'))
        datePosted = input('PastDays(1/3/7/14/dont specify):')
        for offset in range(0, numofPages + 1, 10):
            # print(url)
            params = {
                'q': jobTitle,
                'l': location,
                'jt': jobType,
                'fromage': datePosted,
                'start': offset
            }
            self.get_html(self.url, params)
            time.sleep(random.uniform(1, 2))  # randomly generate float sleep time to
        print("numberofJobs: %d" % self.index)


if __name__ == '__main__':
    start = time.time()
    indeedSpider = IndeedSpider()
    indeedSpider.run()
    end = time.time()
    print('used time: %.2f' % (end - start))

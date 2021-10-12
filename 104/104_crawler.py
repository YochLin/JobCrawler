import json
import requests
import time
from datetime import datetime

import pymongo
from pymongo import MongoClient
from fake_useragent import UserAgent


class Crawler104():
  def __init__(self, db_collection):
    self.url = "https://www.104.com.tw/jobs/search/list?ro=0&jobcat={}&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area={}&order=11&asc=0&page={}&mode=s&jobsource=2018indexpoc"
    self.referer = "https://www.104.com.tw/jobs/search/?ro=0&jobcat={}&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area={}&order=11&asc=0&page={}&mode=s&jobsource=2018indexpoc"
    self.total_page = 0
    self.count = 1
    self.ua = UserAgent()
    self.db_collection = db_collection
    self.db_collection.create_index([('jobNo', pymongo.ASCENDING)], unique=True)    ## create a unique index on a key that rejects documents whose value for that key already exists in the index.

  def parse_json(self, json_104):
    data = json_104["data"]
    job_list = data["list"]
    self.total_page = int(data["totalPage"])
    for i, job in enumerate(job_list):
      job["date"] = datetime(int(job["appearDate"][:4]), int(job["appearDate"][4:6]), int(job["appearDate"][6:]))
      try:
        save_data(self.db_collection, job)
      except pymongo.errors.DuplicateKeyError:
        print("Not save jobNo {}".format(job['jobNo']))
    # save_data(self.db_collection, job_list, True)
    print("Save page {}".format(self.count))
      

  
  def crawler(self):
    user_agent = self.ua.random
    self.job_filter()
    while True:
      header = {"User-Agent": user_agent, "Referer": self.referer.format(self.job, self.area, self.count - 1)}
      respone = requests.get(self.url.format(self.job, self.area,self.count), headers=header)
      self.parse_json(respone.json())
      print(user_agent)
      if self.count == self.total_page:
        break
      # if self.count % 5 == 0:
      #   user_agent = self.ua.random

      self.count += 1
      time.sleep(2)

  def job_filter(self, job_category=['資訊軟體系統類', '研發相關類'], job_area=["台北市", "新北市", "基隆市"]):
    """
    資訊軟體系統類、研發相關類
    """
    self.job = ""
    with open("jobCat.json", "r", encoding='utf-8') as json_file:
      jobCat = json.load(json_file)
      if len(job_category) > 1:
        for j in job_category:
          self.job += jobCat[j]
          self.job += "%2C"
        self.job = self.job[:-3]
      else:
        self.job = jobCat[job_category[0]]
    
    self.area = ""
    with open("jobArea.json", "r", encoding='utf-8') as json_file:
      jobArea = json.load(json_file)
      if len(job_area) > 1:
        for j in job_area:
          self.area += jobArea[j]
          self.area += "%2C"
        self.area = self.area[:-3]
      else:
        self.area = jobArea[job_area[0]]

def save_data(db_collection, post, multi_insert=False):
  if multi_insert:
    db_collection.insert_many(post)
  else:
    db_collection.insert_one(post)

if __name__ in "__main__":
  
  # ua = UserAgent()
  # user_agent = ua.random
  # print("Fake user agent", user_agent)

  db_url = 'mongodb://%s:%s@%s:%s/' %('dbadmin', '1234', 'localhost', '27017')
  client = MongoClient(db_url)
  jb = client["104_job"]
  collection = jb['jobInformation']
  


  crawler_104 = Crawler104(collection)
  crawler_104.crawler()


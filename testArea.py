import random as rand
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup as bs
import os
from pathlib import Path

x = datetime.datetime.strptime("9-24-2024", "%m-%d-%Y")
y = datetime.datetime.strptime("10-25-2024", "%m-%d-%Y")



onemonth = x-datetime.timedelta(days=31)
threemonth = x-datetime.timedelta(days=63)
oneyear = x-datetime.timedelta(days=365)

#print(datetime.timedelta(days=31))

#today = datetime.datetime.today()
x = pd.read_csv("cardListFile.csv", delimiter="|")
#x["date"] = pd.to_datetime(x["date"], format="%Y-%m-%d")
#x["delta"] = x["date"].apply(lambda x: today - x)
#print(x["delta"])
#print(x.loc[(x["type"]=="Effect Monster") & (x["code"]==17535764)])

print(len(list(set(x["tag1"].to_list()))))
#Path("dataframes").mkdir(parents=True, exist_ok=True)
#os.makedirs("dataframes/"+"dog", exist_ok=True)
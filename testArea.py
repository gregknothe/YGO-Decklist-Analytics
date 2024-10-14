import random as rand
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup as bs
import os
from pathlib import Path
import numpy as np

"""
x = datetime.datetime.strptime("9-24-2024", "%m-%d-%Y")
y = datetime.datetime.strptime("10-25-2024", "%m-%d-%Y")

onemonth = x-datetime.timedelta(days=31)
threemonth = x-datetime.timedelta(days=63)
oneyear = x-datetime.timedelta(days=365)

print(datetime.timedelta(days=31))

today = datetime.datetime.today()
x = pd.read_csv("cardListFile.csv", delimiter="|")
x["date"] = pd.to_datetime(x["date"], format="%Y-%m-%d")
x["delta"] = x["date"].apply(lambda x: today - x)
print(x["delta"])
print(x.loc[(x["type"]=="Effect Monster") & (x["code"]==17535764)])

print(len(list(set(x["tag1"].to_list()))))
Path("dataframes").mkdir(parents=True, exist_ok=True)
os.makedirs("dataframes/"+"dog", exist_ok=True)
"""


#x = pd.read_csv("dataframes/SnakeEye/TCG_100000 days_main_deck.csv", sep="|").fillna("")
#x["deckID"] = x["deckID"].apply(pd.to_numeric)
#y = x[x["name"]=="WANTED: Seeker of Sinful Spoils"]
#z = y["deckID"].to_list()

#print(z)
#y.to_csv("tersttestets.csv",sep="|")

'''
savedID = z[0]
count = 0
idList = []
countList = []
for g in range(len(z)):
    if savedID == 446410:
        print("dog")
    if z[g] != savedID:
        if savedID == 446410:
            print(z[g])
            print(count)
            print(countList)
        savedID = z[g]
        idList.append(z[g])
        countList.append(count)
        count = 1
    else:
        count += 1

#print(len(idList))
#print(len(countList))
print(np.mean(countList))

df = pd.DataFrame({"id": idList, "count": countList})
tf = df[df["count"]>3]
print(tf.reset_index(drop=True))


print(len(z)/len(list(set(list(y["deckID"])))))
'''



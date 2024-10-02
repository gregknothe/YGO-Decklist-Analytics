import pandas as pd
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup as bs
import datetime
import numpy as np
import os
from pathlib import Path
from collections import Counter


def getPageURL(offset=0, limit=20000):
    #Creates list with URL for each decklist on page.
    url = "https://ygoprodeck.com/api/decks/getDecks.php?tournament=tier-2&offset=" + str(offset) + "&limit=" + str(limit)
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = str(bs(webpage, features="lxml"))
    deckURLs = html.split('"pretty_url":"')
    for x in range(len(deckURLs)):
        deckURLs[x] = deckURLs[x].split('"')[0]
    deckURLs.pop(0)
    return deckURLs

def createURL(limit=200000, filename="urlList.csv"):
    #Creates a csv file with URL for each topping decklist.
    urlList = []
    for x in range(round(limit/20)+1):
        try:
            urlList.extend(getPageURL(offset=(x*20), limit=limit))
            if x%20 == 0:
                print(str(x) + ": " + str(urlList[-1]))
        except:
            break
    df = pd.DataFrame({'url': urlList})
    if filename == "new":
        return df
    else:
        id = []
        for x in df["url"].to_list():
            id.append(int(np.char.rpartition(x, "-")[2]))
        df["id"] = id
        df = df.drop_duplicates()
        df = df.sort_values(by="id", ascending=True)
        df.to_csv(filename, sep='|', index=False)
        return

def updateURL(limit=200000, filename="urlList.csv"):
    #Updates existing deck URL file with newly added decks. Returns list of URLs of new decks.
    oldList = pd.read_csv("urlList.csv", sep="|")
    newList = createURL(limit=limit, filename="new")
    new = newList["url"].to_list()
    old = oldList["url"].to_list()
    diff = list(set(new)-set(old))
    if len(diff) > 0:
        print("--New decklist being added:")
        for currDeck in diff:
            oldList.loc[len(oldList.index)] = [currDeck, int(np.char.rpartition(currDeck, "-")[2])]
            print(currDeck)
    else:
        print("--No new decklist available.")
    
    oldList = oldList.sort_values(by="id", ascending=True)

    oldList.to_csv(filename, sep="|", index=False)
    oldList.tail(len(diff)).to_csv("newURLList.csv", sep="|", index=False)
    return diff

def getDeckList(url, id):
    #scrapes the decklist from the URL and returns a dataframe with all cards and deck metadata
    url = "https://ygoprodeck.com/deck/" + url
    req = requests.get(url, headers={'User-Agent': 'XYZ/3.0'}).text
    html = bs(req, features="lxml")
    
    date = html.find(class_="deck-metadata-info").find_all("span")[len(html.find(class_="deck-metadata-info").find_all("span"))-1].get_text()
    date = date[1:].replace("st","").replace("nd","").replace("rd","").replace("th","")
    formatedDate = datetime.datetime.strptime(date, '%b %d %Y')

    tagAndFormat = html.find(class_="deck-metadata-container deck-bgimg").find_all("a")
    format, formatFlag, tags = "", 0, []
    for x in range(len(tagAndFormat)):
        if formatFlag == 1:
            tags.append(tagAndFormat[x].get_text())
        if tagAndFormat[x].get_text() == "Tournament Meta Decks":
            format = "TCG"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Tournament Meta Decks OCG":
            format = "OCG"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Tournament Meta Decks OCG (Asian-English)":
            format = "OCG(Asia-English)"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Tournament Meta Decks Worlds":
            format = "Worlds(TCG)"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Master Duel Decks":
            format = "Worlds(MasterDuel)"
            formatFlag = 1
        elif tagAndFormat[x].get_text() == "Non-Meta Decks":
            format = "undefined"
            formatFlag = 1

    
    nameList, typeList, deckList, codeList, imgSourceList, count = [], [], [], [], [], []
    for deckType in ["main_deck", "extra_deck", "side_deck"]:
        for type in html.find_all(id=deckType):
            for types in type.find_all(class_="lazy"):
                nameList.append(types.get("data-cardname"))
                typeList.append(types.get("data-cardtype"))
                codeList.append(types.get("data-name"))
                imgSourceList.append(types.get("data-src"))
                deckList.append(deckType)
    
    tagLen = len(tags)
    tag1, tag2, tag3 = "", "", ""
    if tagLen >= 1:
        tag1 = tags[0]
    if tagLen >= 2:
        tag2 = tags[1]
    if tagLen == 3:
        tag3 = tags[2]

    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList})
    df["deckID"], df["date"], df["format"], df["tag1"], df["tag2"], df["tag3"] = id, formatedDate, format, tag1, tag2, tag3
    return df

def createCardList(urlListFile, cardListFile=""):
    urlDF = pd.read_csv(urlListFile, delimiter="|")
    urlList = urlDF["url"].to_list()
    idList = urlDF["id"].to_list()
    decklistDF = getDeckList(urlList[0], idList[0])
    for x in range(1, len(urlList)):
        decklist = getDeckList(urlList[x], idList[x])
        decklistDF = pd.concat([decklistDF, decklist])
        if x%20 == 0:
            print(str(x) + ": " + str(urlList[x]))
    decklistDF = decklistDF.reset_index(drop=True)
    if cardListFile != "":
        decklistDF.to_csv(cardListFile, sep='|', index=False)
    return decklistDF

def updateCardList(newURLListFile, cardListFile):
    decklistDF = pd.read_csv(cardListFile, delimiter="|")
    newdeckListDF = createCardList(newURLListFile)
    newdeckListDF["date"] = pd.to_datetime(newdeckListDF["date"]).dt.date
    decklistDF = pd.concat([decklistDF, newdeckListDF])
    decklistDF.to_csv(cardListFile, sep='|', index=False)
    return


#createURL()
#createCardList("urlList.csv", "cardListFile.csv")

#updateURL(40)
#updateCardList("newURLList.csv", "cardListFile.csv")

#x = pd.read_csv("cardListFile.csv", delimiter="|")
#print(x[x["format"].isna()].reset_index(drop=True).to_csv("issueList.csv", sep="|"))


#print(getDeckList("therion-horus-350696", "350696"))

def deckPartitioner():
    x = pd.read_csv("cardListFile.csv", delimiter="|")
    x["date"] = pd.to_datetime(x["date"])
    mainArchetypeList = list(set(x["tag1"].to_list()))
    #mainArchetypeList = ["Snake-Eye", "Melodious", "Mikanko"]
    #mainArchetypeList = ["Snake-Eye"]
    subArchetypeList = list(set(x["tag2"].to_list() + x["tag3"].to_list()))
    today = datetime.datetime.today()
    num = 1
    print("Total Archetypes: " + str(len(list(set(x["tag1"].to_list())))))
    for archetype in mainArchetypeList:
        #typeDF = x[x["tag1"] == archetype]
        archetypeName = "".join(x for x in str(archetype) if x.isalnum())
        print(str(num) + " " + str(archetypeName))
        num += 1
        for formats in ["TCG", "OCG"]:
            #formatDF = typeDF[typeDF["format"] == formats]
            for timeFrame in [datetime.timedelta(days=31), datetime.timedelta(days=93), datetime.timedelta(days=365), datetime.timedelta(days=100000)]:
                #timeDF = formatDF[today - formatDF["date"] <= timeFrame]
                for deckType in ["main_deck", "extra_deck", "side_deck"]:
                    os.makedirs("dataframes/"+archetypeName, exist_ok=True)
                    #df = timeDF[timeDF["deck"]== deckType]
                    df = x[(x["tag1"]==archetype) & (x["format"]==formats) & (today - x["date"] <= timeFrame) & (x["deck"]==deckType)]
                    df.to_csv("dataframes/"+archetypeName+"/"+formats+"_"+str(timeFrame).split(",")[0]+"_"+deckType+".csv", sep="|", index=False)
    return

#deckPartitioner()

def codeCorrector(df):
    nameList = list(set(df["name"].to_list()))
    for name in nameList:
        if name == "":
            break
        else:
            subDF = df[df["name"]==name].sort_values(by="code")
            minID = min(subDF["code"].to_list())
            indexList = subDF.index
            subDF = subDF.reset_index(drop=True)
            imgSource = subDF["imgSource"].iloc[0]
            for index in indexList:
                df.at[index, "code"] = minID
                df.at[index, "imgSource"] = imgSource
    return df

def deckAnalytics():
    #x = pd.read_csv("dataframes/Melodious/TCG_93 days_main_deck.csv", sep="|").fillna("")
    x = pd.read_csv("dataframes/SnakeEye/TCG_93 days_main_deck.csv", sep="|").fillna("")
    #x = pd.read_csv("dataframes/SnakeEye/TCG_100000 days_main_deck.csv", sep="|").fillna("")
    #x = pd.read_csv("dataframes/SnakeEye/TCG_100000 days_main_deck.csv", sep="|").fillna("")
    #x = pd.read_csv("dataframes/SnakeEye/TCG_100000 days_side_deck.csv", sep="|").fillna("")
    #x = pd.read_csv("dataframes/SnakeEye/TCG_100000 days_extra_deck.csv", sep="|").fillna("")
    cardIDList = list(set(x["code"].to_list()))
    cardNameList = list(set(x["name"].to_list()))
    if len(cardIDList) != len(cardNameList):
        x = codeCorrector(x)
        cardIDList = list(set(x["code"].to_list()))
        #print(x[x["name"]=="Ash Blossom & Joyous Spring"])
    totalDeckCount = len(list(set(x["deckID"].to_list())))
    cardDeckCount, cardAvgCount, cardName, cardImgSource = [], [], [], []
    for cardID in cardIDList:
        cardDF = x[x["code"]==cardID].reset_index(drop=True)
        cardDeckList = list(set(cardDF["deckID"].to_list()))
        cardAvgCount.append(round(np.mean(list(Counter(cardDF["deckID"]).values())),3))
        cardDeckCount.append(len(cardDeckList))
        cardImgSource.append(cardDF["imgSource"].iloc[0])
        #cardDeckCount.append()
        cardName.append(x.loc[x["code"]==cardID, "name"].iloc[0])
    df = pd.DataFrame({"code": cardIDList, "deckCount": cardDeckCount, "imgSource": cardImgSource, "avgCount": cardAvgCount})
    df["deckPerc"] = round(df["deckCount"] / totalDeckCount, 3)
    #df = df.drop(columns=["deckCount"])
    df["name"] = cardName
    
    df = df[["name", "code", "imgSource", "deckPerc", "avgCount"]].sort_values(["deckPerc", "avgCount"], ascending=False).reset_index(drop=True)
    print(df.to_string())
    return

deckAnalytics()

#x = pd.read_csv("dataframes/Melodious/TCG_93 days_main_deck.csv", sep="|")
'''
cardIDList = list(set(x["code"].to_list()))
cardNameList = list(set(x["name"].to_list()))
print(cardIDList)
pd.DataFrame({"name": cardNameList}).to_csv("nametest.csv", index=False)
pd.DataFrame({"id": cardIDList}).to_csv("idtest.csv", index=False)
print(cardNameList)
'''
#x = codeCorrector(x)
#x = x[x["name"]=="Ash Blossom & Joyous Spring"]
#print(x)

#--------------------------Clean Set Up---------------------------------            446394
#createURL() #4:35
#createCardList("urlList.csv", "cardListFile.csv") #1:30:23


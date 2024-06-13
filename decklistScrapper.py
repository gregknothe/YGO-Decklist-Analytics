import pandas as pd
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import urllib3
import lxml.html
import requests

pd.options.mode.chained_assignment = None  # default='warn'
"""
Get multiple deck list, split the list into deck types (main, extra, side) then calc the below stats per card:
-% of selected decks running this card
-Average # of copies ran
-Basic stats (name, card type, code, imgSource)
-Sort list based on the % of decks running, then by # of copies 
Compile the list together (main, extra, side) and we are done pretty much
"""


deckURL = "https://ygoprodeck.com/deck/mikanko-dogmatika-471741"
searchURL = "https://ygoprodeck.com/deck-search/#&cardcode=Ashoka%20Pillar%7CHa-Re%20the%20Sword%20Mikanko%7C&tournament=tier-2&from=2023-12-01&to=2024-06-12&offset=0"
#searchURL = "https://ygoprodeck.com/api/decks/getDecks.php?&cardcode=Ashoka%20Pillar%7CHa-Re%20the%20Sword%20Mikanko%7C&tournament=tier-2&from=2023-12-01&to=2024-06-12&limit=20&offset=0"
SESearch = "https://ygoprodeck.com/deck-search/#&cardcode=Snake-Eyes%20Poplar%7C&tournament=tier-2&offset=0"

def decklistScrape(url):
    #Scrapes the decklist from the URL and returns a dataframe with:
    #name of card, type of card, deck (main, extra, side), card code, image url of card
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = bs(webpage, features="lxml")
    nameList, typeList, deckList, codeList, imgSourceList, count = [], [], [], [], [], []
    for deckType in ["main_deck", "extra_deck", "side_deck"]:
        for tag in html.find_all(id=deckType):
            for tags in tag.find_all(class_="lazy master-duel-card"):
                #print(tags)
                #nameList.append(str(tags).split('data-cardname="')[1].split('"')[0])
                nameList.append(tags.get("data-cardname"))
                typeList.append(tags.get("data-cardtype"))
                codeList.append(tags.get("data-name"))
                imgSourceList.append(tags.get("data-src"))
                deckList.append(deckType)
                count.append(1)
    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList, "count": count})
    return df

#print(decklistScrape("https://ygoprodeck.com/deck/fiendsmith-snake-eye-501145"))
#print(decklistScrape(deckURL))

def getDeckURL(url, offset=0, limit=100):
    #Modifies the search url to the api call, then returns the deck list urls from the search.
    url = url.replace("https://ygoprodeck.com/deck-search/#", "https://ygoprodeck.com/api/decks/getDecks.php?").replace("&offset=0", "&limit="+str(limit)+"&offset="+str(offset))
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = str(bs(webpage, features="lxml"))
    deckURLs = html.split('"pretty_url":"')
    for x in range(len(deckURLs)):
        deckURLs[x] = deckURLs[x].split('"')[0]
    deckURLs.pop(0)
    return deckURLs

#print(getDeckURL(searchURL))

def getDeckURLs(url, limit=100):
    #Gets all deck urls from search results. Does round up limit to the nearest 20s to make it easier.
    urlList = []
    for x in range(round(limit/20)+1):
        try:
            urlList.append(getDeckURL(url, offset=(x*20), limit=limit))
        except:
            break
    allurls = [j for i in urlList for j in i]
    return allurls
    
#x = getDeckURLs("https://ygoprodeck.com/deck-search/#&cardcode=Snake-Eyes%20Poplar%7C&tournament=tier-2&offset=0",limit=25)
#x = getDeckURLs(searchURL,limit=205)
#print(x)
#print(len(x))

def getStats(url, limit=100):
    urls = getDeckURLs(url, limit=limit)
    decklists = []
    for url in urls:
        #Gathers the decklists for all the decks
        decklists.append(decklistScrape("https://ygoprodeck.com/deck/"+url))
    counts = []
    for decklist in decklists:
        #Calculates the counts for each card in each list
        values = decklist.groupby(["name", "deck", "type", "code", "imgSource"]).count().sort_values(by=["deck"])
        values.reset_index(inplace=True)
        counts.append(values)
    #print(counts)
    mainName, mainDeck, mainType, mainCode, mainImgSource, mainCount, mainApperances = [], [], [], [], [], [], []
    maindf = pd.DataFrame({"name": mainName, "deck": mainDeck, "type": mainType, "code": mainCode, "imgSource": mainImgSource, "count": mainCount, "apperances": mainApperances})
    extraName, extraDeck, extraType, extraCode, extraImgSource, extraCount, extraApperances = [], [], [], [], [], [], []
    extradf = pd.DataFrame({"name": extraName, "deck": extraDeck, "type": extraType, "code": extraCode, "imgSource": extraImgSource, "count": extraCount, "apperances": extraApperances})
    sideName, sideDeck, sideType, sideCode, sideImgSource, sideCount, sideApperances = [], [], [], [], [], [], []
    sidedf = pd.DataFrame({"name": sideName, "deck": sideDeck, "type": sideType, "code": sideCode, "imgSource": sideImgSource, "count": sideCount, "apperances": sideApperances})
    for count in counts:
        #Takes each decklist (with counts) and seperates them into the main, extra, and side list. 
        main = count[count["deck"]=="main_deck"].reset_index(drop=True)
        extra = count[count["deck"]=="extra_deck"].reset_index(drop=True)
        side = count[count["deck"]=="side_deck"].reset_index(drop=True)
        for card in range(len(main["name"])):
            if main["name"][card] in list(maindf["name"]):
                loc = maindf.index[maindf["name"]==main["name"][card]]
                maindf["count"][loc] = maindf["count"][loc] + main["count"][card]
                maindf["apperances"][loc] = maindf["apperances"][loc] + 1
            else:
                maindf.loc[len(maindf.index)] = [main["name"][card], "main_deck", main["type"][card], main["code"][card], main["imgSource"][card], main["count"][card], 1]
        for card in range(len(extra["name"])):
            if extra["name"][card] in list(extradf["name"]):
                loc = extradf.index[extradf["name"]==extra["name"][card]]
                extradf["count"][loc] = extradf["count"][loc] + extra["count"][card]
                extradf["apperances"][loc] = extradf["apperances"][loc] + 1
            else:
                extradf.loc[len(extradf.index)] = [extra["name"][card], "extra_deck", extra["type"][card], extra["code"][card], extra["imgSource"][card], extra["count"][card], 1]
        
        for card in range(len(side["name"])):
            if side["name"][card] in list(sidedf["name"]):
                loc = sidedf.index[sidedf["name"]==side["name"][card]]
                sidedf["count"][loc] = sidedf["count"][loc] + side["count"][card]
                sidedf["apperances"][loc] = sidedf["apperances"][loc] + 1
            else:
                sidedf.loc[len(sidedf.index)] = [side["name"][card], "side_deck", side["type"][card], side["code"][card], side["imgSource"][card], side["count"][card], 1]

    finalDF = pd.concat([maindf, extradf, sidedf]).reset_index(drop=True)
    finalDF["avgCopies"] = finalDF.apply(lambda x: x["count"] if x["count"] < 1 else round(x["count"]/x["apperances"],2), axis=1)
    finalDF["percOfDecks"] = round(finalDF["apperances"] / len(urls),2)

    finalDF["deck"] = pd.Categorical(finalDF["deck"], ["main_deck", "extra_deck", "side_deck"])
    finalDF["type"] = pd.Categorical(finalDF["type"], ["Normal Monster", "Effect Monster", "Tuner Monster", "Ritual Normal Monster", "Ritual Effect Monster", "Fusion Monster",
                                                       "Synchro Monster", "XYZ Monster", "Link Monster", "Spell Card", "Trap Card"])

    return finalDF.sort_values(["deck", "type", "percOfDecks", "avgCopies"], ascending=[True, True, False, False])


test = "https://ygoprodeck.com/deck-search/#&cardcode=Ashoka%20Pillar%7CHa-Re%20the%20Sword%20Mikanko%7CInstant%20Fusion%7C&tournament=tier-2&from=2023-12-01&to=2024-06-12&offset=0"
print(getStats(SESearch,30).to_string())
#x = getStats(searchURL,10)
#print(x)
#print(x.index.values)
#print(x["type"].values)

#Make new variable for monster, spell and trap for more logical sorting
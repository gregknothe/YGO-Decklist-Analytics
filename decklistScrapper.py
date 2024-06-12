import pandas as pd
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import urllib3
import lxml.html
import requests


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
    nameList, typeList, deckList, codeList, imgSourceList = [], [], [], [], []
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
    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList})
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
    print(urls)
    for url in urls:
        print(decklistScrape("https://ygoprodeck.com/deck/"+url))
    return

getStats(SESearch,10)
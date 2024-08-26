import pandas as pd
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime


def decklistScrape(url):
    #scrapes the decklist from the URL and returns a dataframe with all cards and deck metadata
    req = requests.get(url, headers={'User-Agent': 'XYZ/3.0'}).text
    html = bs(req, features="lxml")

    #deck metadata
    deckID = url.split("-")[len(url.split("-"))-1]
    date = html.find(class_="deck-metadata-info").find_all("span")[len(html.find(class_="deck-metadata-info").find_all("span"))-1].get_text()
    date = date[1:].replace("st","").replace("nd","").replace("rd","").replace("th","")
    formatedDate = datetime.strptime(date, '%b %d %Y')

    #individual card data
    nameList, typeList, deckList, codeList, imgSourceList, count = [], [], [], [], [], []
    for deckType in ["main_deck", "extra_deck", "side_deck"]:
        for tag in html.find_all(id=deckType):
            for tags in tag.find_all(class_="lazy"):
                nameList.append(tags.get("data-cardname"))
                typeList.append(tags.get("data-cardtype"))
                codeList.append(tags.get("data-name"))
                imgSourceList.append(tags.get("data-src"))
                deckList.append(deckType)
                count.append(1)
    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList, "count": count})
    df["deckID"], df["date"] = deckID, formatedDate
    return df

#url = "https://ygoprodeck.com/deck/branded-despia-520607"
#print(decklistScrape(url))
#print(decklistScrape(url))

def getDeckURL(url, offset=0, limit=100):
    #Modifies the search url to the api call, then returns the deck list urls from the search.
    url = url.replace("https://ygoprodeck.com/deck-search/#", "https://ygoprodeck.com/api/decks/getDecks.php?").replace("https://ygoprodeck.com/deck-search/?", "https://ygoprodeck.com/api/decks/getDecks.php?").replace("&offset=0", "&limit="+str(limit)+"&offset="+str(offset))
    req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
    webpage = urlopen(req, timeout=10).read()
    html = str(bs(webpage, features="lxml"))
    deckURLs = html.split('"pretty_url":"')
    for x in range(len(deckURLs)):
        deckURLs[x] = deckURLs[x].split('"')[0]
    deckURLs.pop(0)
    return deckURLs

print(getDeckURL("https://ygoprodeck.com/tournaments/top-archetypes/"))


#Get urls by tag (allows for tag analysis)
#Get the urls from the page (requires api stooping.)
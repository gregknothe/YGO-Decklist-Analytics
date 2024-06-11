import pandas as pd
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

deckURL = "https://ygoprodeck.com/deck/mikanko-dogmatika-471741"

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
                nameList.append(str(tags).split('data-cardname="')[1].split('"')[0])
                typeList.append(str(tags).split('data-cardtype="')[1].split('"')[0])
                codeList.append(str(tags).split('data-name="')[1].split('"')[0])
                imgSourceList.append(str(tags).split('data-src="')[1].split('"')[0])
                deckList.append(deckType)
    df = pd.DataFrame({"name": nameList, "type": typeList, "deck": deckList, "code": codeList, "imgSource": imgSourceList})
    return df

#print(decklistScrape(deckURL))

"""
Get multiple deck list, split the list into deck types (main, extra, side) then calc the below stats per card:
-% of selected decks running this card
-Average # of copies ran
-Basic stats (name, card type, code, imgSource)
-Sort list based on the % of decks running, then by # of copies 
Compile the list together (main, extra, side) and we are done pretty much
"""




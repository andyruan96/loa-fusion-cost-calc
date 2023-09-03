import requests
import json
from enum import StrEnum
from tabulate import tabulate

COST_REDUCTION = 0.0

class Item(StrEnum):
    PrimeOreha = '6861011'
    SuperiorOreha = '6861009'
    WhiteRelic = '6882701'
    GreenRelic = '6885508'
    BlueRelic = '6882605'
    WhiteFish = '6882601'
    GreenFish = '6882002'
    BlueFish = '6885708'
    WhiteMeat = '6882304'
    GreenMeat = '6882505'
    BlueMeat = '6885608'

class Keys(StrEnum):
    AvgPrice = 'avgPrice'
    LowPrice = 'lowPrice'

class Costs:
    def __init__(self, blue: int, green: int, white: int, priceBlue: float, priceGreen: float, priceWhite: float, goldCost: int, quantityCrafted: int):
        self.blue = blue
        self.green = green
        self.white = white
        self.priceBlue = priceBlue
        self.priceGreen = priceGreen
        self.priceWhite = priceWhite
        self.goldCost = goldCost
        self.quantityCrafted = quantityCrafted

    def getPriceForCraft(self):
        return round(self.blue * self.priceBlue / 10) + round(self.green * self.priceGreen / 10) + round(self.white * self.priceWhite / 100) + round(self.goldCost * (1-COST_REDUCTION))

class OrehaCosts:
    def __init__(self, relic: Costs, fish: Costs, meat: Costs):
        self.relic = relic
        self.fish = fish
        self.meat = meat
        

class MaterialCosts:
    def __init__(self, primePrice: int, superiorPrice: int, prime: OrehaCosts, superior: OrehaCosts):
        self.primePrice = primePrice
        self.superiorPrice = superiorPrice
        self.prime = prime
        self.superior = superior

    def printCostReport(self):
        headers = ['Mat', 'Crafting Cost', 'Market Value', 'Craft Adv']
        superiorData = [
            ['Relic', *self._getRowData(self.superior.relic, self.superiorPrice) ],
            ['Fish', *self._getRowData(self.superior.fish, self.superiorPrice) ],
            ['Meat', *self._getRowData(self.superior.meat, self.superiorPrice) ],
        ]
        primeData = [
            ['Relic', *self._getRowData(self.prime.relic, self.primePrice) ],
            ['Fish', *self._getRowData(self.prime.fish, self.primePrice) ],
            ['Meat', *self._getRowData(self.prime.meat, self.primePrice) ],
        ]

        print(f'=== Prime {self.primePrice}g ===')
        print(tabulate(primeData, headers))
        print(f'=== Superior {self.superiorPrice}g ===')
        print(tabulate(superiorData, headers))
    
    def _getRowData(self, costs: Costs, fusionPrice: int):
        craftingCost = costs.getPriceForCraft()
        marketValue = costs.quantityCrafted * fusionPrice
        craftingAdv = (marketValue - craftingCost) / marketValue
        return [craftingCost, marketValue, f'{craftingAdv:.2%}']


itemList = [e.value for e in Item]
query = ','.join(itemList)
response = requests.get(f'https://www.lostarkmarket.online/api/export-market-live/North%20America%20West?ids={query}')

responseBody = response.json()
# print(json.dumps(responseBody, indent=2))
responseItemCodes = list(map(lambda x : x['gameCode'], responseBody))
itemDict = dict(zip(responseItemCodes, responseBody))


materialCosts = MaterialCosts(
    itemDict[Item.PrimeOreha][Keys.LowPrice],
    itemDict[Item.SuperiorOreha][Keys.LowPrice],
    OrehaCosts(
        Costs(52, 51, 107, itemDict[Item.BlueRelic][Keys.LowPrice], itemDict[Item.GreenRelic][Keys.LowPrice], itemDict[Item.WhiteRelic][Keys.LowPrice], 300, 15),
        Costs(52, 69, 142, itemDict[Item.BlueFish][Keys.LowPrice], itemDict[Item.GreenFish][Keys.LowPrice], itemDict[Item.WhiteFish][Keys.LowPrice], 300, 15),
        Costs(52, 69, 142, itemDict[Item.BlueMeat][Keys.LowPrice], itemDict[Item.GreenMeat][Keys.LowPrice], itemDict[Item.WhiteMeat][Keys.LowPrice], 300, 15)
    ),
    OrehaCosts(
        Costs(16, 29, 94, itemDict[Item.BlueRelic][Keys.LowPrice], itemDict[Item.GreenRelic][Keys.LowPrice], itemDict[Item.WhiteRelic][Keys.LowPrice], 250, 20),
        Costs(16, 64, 128, itemDict[Item.BlueFish][Keys.LowPrice], itemDict[Item.GreenFish][Keys.LowPrice], itemDict[Item.WhiteFish][Keys.LowPrice], 250, 20),
        Costs(16, 64, 128, itemDict[Item.BlueMeat][Keys.LowPrice], itemDict[Item.GreenMeat][Keys.LowPrice], itemDict[Item.WhiteMeat][Keys.LowPrice], 250, 20)
    )
)

materialCosts.printCostReport()

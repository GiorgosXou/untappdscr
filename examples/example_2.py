import distinctipy
from partialformatter import PartialFormatter
from untappdscr       import UntappdScrapper
from colour           import Color
from x256             import x256

BLUE           = '\x1b[38;5;' + str(x256.from_hex('ADD8E6')) + 'm' 
WHITE          = '\x1b[38;5;' + str(x256.from_hex('ffffff')) + 'm'
ORANGE         = '\x1b[38;5;' + str(x256.from_hex('FFD580')) + 'm'
color_gradient = list(Color("red").range_to(Color("green"),50)) # list because python is silly with arrays | i'm gonna puke eew

def get_color_for(value):
    return '\x1b[38;5;' + str(x256.from_hex(color_gradient[int(value*10)].get_hex_l()[1:])) + 'm'


untappd         = UntappdScrapper () 
formatter       = PartialFormatter()
top_breweries   = untappd.get_top_rated_breweries('Greece', picker=True)
categories      = untappd.brewery_picker.types
distinct_colors = distinctipy.get_colors(len(categories)) 
switch          = False
background      = '\033[48;2;40;40;40m' #
category_colors = {}
for i, ctgry in enumerate(categories):
    category_colors[ctgry.replace('_',' ').title()] = '\x1b[38;5;' + str(x256.from_hex(distinctipy.get_hex(distinct_colors[i])[1:])) + 'm'
    
  
print('╭━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮')
print('┃ ## ┃ Beers ┃  Rating  ┃  Ratings  ┃     Category     ┃          Breweryname          ┃              Name              ┃                Location               ┃')
print('┠━━━━╋━━━━━━━╋━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫')
for i, (_, b) in enumerate(top_breweries.items(), 1):
    print(formatter.format("┃ "+ background +"{:<2} ┃ "+ ORANGE +"{:<5}"+ WHITE +" ┃ " + get_color_for(b.details.rating) + "{:<8}" + WHITE + " ┃ {:<9} ┃ " + category_colors[b.details.category] + "{:<16}" + WHITE + " ┃ "+ BLUE +"{:<29}"+ WHITE +" ┃ {:<30} ┃ {:<37}\033[0m ┃", i, b.details.beer_count,b.details.rating,b.details.ratings,b.details.category,b.breweryname[0:29],b.name[0:30],b.details.location[0:37])) 
    if switch: background = '\033[48;2;10;10;10m'
    else:      background = '\033[48;2;0;0;0m'
    switch = not switch
print('╰━━━━┻━━━━━━━┻━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯')
 



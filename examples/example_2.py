from colorhash   import ColorHash
from untappdscr  import UntappdScraper
from colour      import Color
from x256        import x256


BLUE           = '\x1b[38;5;' + str(x256.from_hex('ADD8E6')) + 'm' 
WHITE          = '\x1b[38;5;' + str(x256.from_hex('ffffff')) + 'm'
ORANGE         = '\x1b[38;5;' + str(x256.from_hex('FFD580')) + 'm'
color_gradient = list(Color("red").range_to(Color("green"),51))

def get_color_for(value) : return '\x1b[38;5;' + str(x256.from_hex(color_gradient[int(value)*10].get_hex_l()[1:])) + 'm'
def get_hash_color(value): return '\x1b[38;5;' + str(x256.from_rgb(*ColorHash(value).rgb)) + 'm'

untappd         = UntappdScraper() 
top_breweries   = untappd.get_top_rated_breweries('Greece', picker=True)
categories      = untappd.brewery_picker.types
switch          = False
background      = '\033[48;2;40;40;40m' #
category_colors = {}
  
print('╭━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮')
print('┃ ## ┃ Beers ┃  Rating  ┃  Ratings  ┃     Category     ┃          Breweryname          ┃              Name              ┃                Location               ┃')
print('┠━━━━╋━━━━━━━╋━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫')
for i, (_, b) in enumerate(top_breweries.items(), 1):
    print(str("┃ "+ background +"{:<2} ┃ "+ ORANGE +"{:<5}"+ WHITE +" ┃ " + get_color_for(b.details.rating) + "{:<8}" + WHITE + " ┃ {:<9} ┃ " + get_hash_color(b.details.category) + "{:<16}" + WHITE + " ┃ "+ BLUE +"{:<29}"+ WHITE +" ┃ {:<30} ┃ {:<37}\033[0m ┃").format( i, b.details.beer_count,b.details.rating,b.details.ratings,b.details.category,b.breweryname[0:29],b.name[0:30],b.details.location[0:37]))
    if switch: background = '\033[48;2;10;10;10m'
    else:      background = '\033[48;2;0;0;0m'
    switch = not switch
print('╰━━━━┻━━━━━━━┻━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯')
 



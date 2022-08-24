from partialformatter import PartialFormatter
from untappdscr       import UntappdScrapper


untappd       = UntappdScrapper () 
formatter     = PartialFormatter()
top_breweries = untappd.get_top_rated_breweries('Greece')

print('╭━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮')
print('┃ ## ┃ Beers ┃  Rating  ┃  Ratings  ┃     Category     ┃          Breweryname          ┃              Name              ┃                Location               ┃')
print('┠━━━━╋━━━━━━━╋━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫')
for i, (_, b) in enumerate(top_breweries.items(), 1): # maybe add backgroundcolor per 2 lines to distigues them
    print(formatter.format("┃ {:<2} ┃ {:<5} ┃ {:<8} ┃ {:<9} ┃ {:<16} ┃ {:<29} ┃ {:<30} ┃ {:<37} ┃", i, b.details.beer_count,b.details.rating,b.details.ratings,b.details.category,b.breweryname[0:29],b.name[0:30],b.details.location[0:37])) 
print('╰━━━━┻━━━━━━━┻━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯')
 
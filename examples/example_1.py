from untappdscr import UntappdScraper

untappd = UntappdScraper()
top_breweries = untappd.get_top_rated_breweries('Greece')

print('╭━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮')
print('┃ ## ┃ Beers ┃  Rating  ┃  Ratings  ┃     Category     ┃          Breweryname          ┃              Name              ┃                Location               ┃')
print('┠━━━━╋━━━━━━━╋━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫')
for i, (_, b) in enumerate(top_breweries.items(), 1):
    print("┃ {:<2} ┃ {:<5} ┃ {:<8} ┃ {:<9} ┃ {:<16} ┃ {:<29} ┃ {:<30} ┃ {:<37} ┃".format(i, b.details.beer_count,b.details.rating,b.details.ratings,b.details.category,b.breweryname[0:29],b.name[0:30],b.details.location[0:37])) 
print('╰━━━━┻━━━━━━━┻━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯')

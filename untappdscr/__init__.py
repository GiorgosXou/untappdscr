from   bs4               import BeautifulSoup
from   enum              import Enum
from   time              import sleep
from   random            import randint
from   dacite            import from_dict
from   dataclasses       import dataclass
from   requests.adapters import HTTPAdapter, Retry
import requests
import re



@dataclass
class BreweryPicker:
    countries : list  
    types     : list 
    
@dataclass
class BeerPicker:
    countries : list
    styles    : list

@dataclass      
class Stats: 
    total   : int 
    unique  : int
    monthly : int
    you     : int


class ActivityFilter(Enum):
    GLOBAL  = ''
    FRIENDS = '?filter=friends'
    YOU     = '?filter=you'


# @dataclass      
# class Checkin: # activity-checkins doesn't always have "...at place"
#     user     : 'User'
#     drinking : 'Beer'
#     at       : 'Venue'

@dataclass
class Brewery:
    @dataclass
    class BreweryDetails: #TODO: id from label |  Maybe add a dict of beers out of stats | and maybe add subsidiary too like with /sixpoint | discontinued for /w/brew-it-up/7220 class="oop error" 
        # @dataclass      
        # class BreweryCheckin(Checkin):
        #     pass
        @dataclass      
        class BreweryStats(Stats):
            likes : int         
        logo           : str 
        category       : str
        location       : str
        rating         : float
        ratings        : int
        beer_count     : int
        claimed        : bool    
        popular_venues : dict
        # activity       : dict[int, BreweryCheckin]
        stats          : BreweryStats
    breweryname : str
    name        : str
    details     : BreweryDetails
        
@dataclass
class Beer:
    @dataclass
    class BeerDetails: # TODO: ADD Collaboration? example /3027845
        @dataclass      
        class BeerStats(Stats):
            pass               
        desc_half    : str       # half Descrition
        ABV          : int       # percentage
        IBU          : float
        stats        : BeerStats
        rating       : float     # TODO: ADD a g_rating for global ratings too 
        ratings      : int
        date_added   : str       # MM/DD/YY
        discontinued : bool       
        loyals       : dict     
    id       : int
    name     : str
    brewery  : Brewery
    details  : BeerDetails
    
@dataclass
class Venue:
    @dataclass
    class VenueDetails: # TODO: Add class VenueServingDetails for the actuall details (if not None)?
        @dataclass      
        class VenueStats(Stats):
            pass
        address_name : str
        map_url      : str
        phone        : str
        logo         : str
        info         : str
        stats        : VenueStats # VenueStats
        loyals       : dict # of User(s) # TODO: PATRONS IF NONE because some venues don't have them
    id          : int
    name        : str
    category    : str
    is_verified : bool 
    details     : VenueDetails
        
@dataclass
class User:
    @dataclass
    class UserDetails:
        loyal_to : dict # of Venue(s)
    checkins : int  # from venue
    username : str
    name     : str


class UntappdScraper:
    URL = 'https://untappd.com/'

    def __init__(self, delay=None, max_retries=9, backoff_factor=1.0, debug_mode=False, keep_reference_track=False) -> None:
        self.keep_reference_track = keep_reference_track
        self.users     = {}
        self.beers     = {}
        self.venues    = {}
        self.breweries = {}
        self.cookies   = {}
        self.headers   = { # , 'X-Requested-With': 'XMLHttpRequest'XMLHttpRequest ana 25 mono gia to more_friends?
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36', 
            'X-Requested-With': 'XMLHttpRequest'
        } 
        self.beer_picker     = None
        self.brewery_picker  = None
        self.request_counter = 0    
        self.debug_mode     = debug_mode
        self.delay_range    = delay
        self.max_retries    = max_retries
        self.backoff_factor = backoff_factor


    def __get_data_from(self, url_path, retries=0): # TODO: coockies= login-cockies only for special request
        self.request_counter += 1
        if self.delay_range : sleep(randint(*self.delay_range)) # * tuple
        if self.debug_mode  : print(f'- GET REQUEST #{self.request_counter}: {url_path}')  
        session = requests.Session() # https://stackoverflow.com/a/47475019/11465149
        retry   = Retry(connect = self.max_retries, backoff_factor = self.backoff_factor)
        adapter = HTTPAdapter(max_retries = retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(self.URL + url_path, headers=self.headers,  verify=True, cookies=self.cookies)
        return response.text
    

    def __check_if_page_exits(self, html_doc):
        assert html_doc.find('head').find('title').next not in ('Untappd | 404', 'Untappd | Error'), ValueError(html_doc.find('head').find('title').next) 
    
    
    def __get_document_from(self, url_path):
        html_doc = BeautifulSoup   (self.__get_data_from(url_path), 'html.parser')
        self.__check_if_page_exits (html_doc                                     )
        return html_doc
    
    
    def __float1(self, str_num:str):
        return None if not str_num[-1:].isdecimal() else float(str_num)
    
    
    def __int2  (self, str_num:str):
        return None if not str_num[-1:].isdecimal() else int(str_num)
    
    
    def __int1  (self, str_num:str): # fogor :skull_emoji: if stats.you and have M+ lol
        str_num = str_num.strip().replace(',', '')
        if not str_num[-1:].isdecimal(): # extreme senario but ...
            str_num = str_num.replace('+','') 
            if str_num.endswith('M'):
                str_num = float(str_num[0:-1]) * 1000000    # /topplinggoliathbrewing
            elif str_num.endswith('B'): # THIS IS JUST A GUESS
                str_num = float(str_num[0:-1]) * 1000000000
        return int(str_num)
    
                   
    def __extract_option_items_from(self, element_picker):
        return re.findall(r'data-value-slug="(.*?)"', str(element_picker))


    def get_beer_picker_list(self, htmldoc=None):
        html_doc           = htmldoc or BeautifulSoup (self.__get_data_from('beer/top_rated'), 'html.parser'                                                             )
        elements           = html_doc.findAll         ('select', {'id':('filter_picker','sort_picker')}                                                                  )
        self.beer_picker   = BeerPicker               ( countries = self.__extract_option_items_from(elements[1]), styles = self.__extract_option_items_from(elements[0]))
        return self.beer_picker


    def get_brewery_picker_list(self, htmldoc=None):
        html_doc            = htmldoc or BeautifulSoup (self.__get_data_from('brewery/top_rated'), 'html.parser'                                                          )
        elements            = html_doc.findAll         ('select', {'id':('filter_picker','sort_picker')}                                                                  )
        self.brewery_picker = BreweryPicker            ( countries = self.__extract_option_items_from(elements[0]), types  = self.__extract_option_items_from(elements[1]))
        return self.brewery_picker    
                
                
    def get_picker_lists(self):
        html_doc            = BeautifulSoup    (self.__get_data_from('beer/top_rated') + self.__get_data_from('brewery/top_rated')                                )
        elements            = html_doc.findAll ('select', {'id':('filter_picker','sort_picker')}                                                                  )
        self.beer_picker    = BeerPicker       ( countries = self.__extract_option_items_from(elements[1]), styles = self.__extract_option_items_from(elements[0]))
        self.brewery_picker = BreweryPicker    ( countries = self.__extract_option_items_from(elements[2]), types  = self.__extract_option_items_from(elements[3]))
        return (self.beer_picker, self.brewery_picker) 


    def get_top_rated_breweries(self, country='', type='', picker=False):
        top_rated_breweries = {}
        html_doc            = self.__get_document_from (f'brewery/top_rated?country={country}&brewery_type={type}')
        if picker: self.get_brewery_picker_list(html_doc)
        brewery_container   = html_doc.find            ('div', {'class': 'beer-container beer-list'})
        for brewery_item in brewery_container.findAll('div', {'beer-item'}               ):
            details         = brewery_item   .find   ('div', {'class': 'details brewery'})
            brewery_details = brewery_item   .find   ('div')
            breweryname     = brewery_details.find   ('a'  ).attrs['href'][1:]
            type_location   = brewery_details.findAll('p'  )
            brewery_dict    = {  
                'name'        : brewery_details.find('a').next ,
                'breweryname' : breweryname                    ,
                'details'     : Brewery.BreweryDetails(
                    category       =       type_location[2].next                                                                           ,
                    location       =       type_location[1].next                                                                           ,   
                    logo           =       brewery_item.find('img').attrs['src']                                                           ,
                    rating         = float(details     .find('div', {'class': 'caps'}).attrs['data-rating'])                               ,
                    ratings        = int  (details     .find('p'  , {'class': 'ibu' }).next.strip().split(' ')[0].strip().replace(',','')) , # TODO: check for changes, SuS class-name called ibu
                    beer_count     = int  (details     .find('p'  , {'class': 'abv' }).next.strip().split(' ')[0].strip().replace(',','')) , # You never know.. a brewery might produce over 999 beers xD | 13 for some reason had a space that trim didn't get
                    claimed        = None                                                                                                  ,
                    popular_venues = None                                                                                                  , # At the momment 
                    stats          = None
            )   }
            if not self.keep_reference_track:
                top_rated_breweries[breweryname] = from_dict(Brewery, brewery_dict)
                continue
            brewery = self.breweries.get(breweryname)
            if brewery: 
                if brewery.details:
                    brewery_dict['details'].claimed        = brewery.details.claimed 
                    brewery_dict['details'].popular_venues = brewery.details.popular_venues 
                    brewery_dict['details'].stats          = brewery.details.stats 
                brewery                            .__dict__.update(brewery_dict)
            else:  self.breweries[breweryname] = from_dict(Brewery, brewery_dict)
            top_rated_breweries  [breweryname] = self.breweries[breweryname]            
        return top_rated_breweries   
            

    def get_top_rated_beers(self, country='', style='', picker=False): # GLOBAL BEERS TOO ETSI
        top_rated_beers = {}
        html_doc        = self.__get_document_from (f'beer/top_rated?type={style}&country={country}')
        if picker: self.get_beer_picker_list(html_doc)
        beer_container  = html_doc.find('div', {'class': 'beer-container beer-list pad'}) #beer-container beer-list pad
        for beer_item in beer_container.findAll('div', {'beer-item'}):
            _id          = int              (beer_item.attrs['data-bid']                   )
            beer_details = beer_item.findAll('p'  , {'class': ('name','style', 'details') })
            description  = beer_item.find   ('p'  , {'class': 'desc desc-half-' + str(_id)})
            details      = beer_item.find   ('div', {'class': 'details'                   })
            breweryname  = beer_details[1].contents[0].attrs['href'][1:] 
            brebery_obj  = Brewery(  
                breweryname = breweryname                             ,                           
                name        = beer_details[1].contents[0].contents[0] ,
                details     = None                                    ,
            )
            if self.keep_reference_track: self.breweries[breweryname] = self.breweries.get(breweryname) or brebery_obj
            beer_dict   = { # I won't use if because ratings can change + other stuff
                'id'      : _id                                     ,
                'name'    : beer_details[0].contents[0].contents[0] ,
                'brewery' : self.breweries[breweryname] if self.keep_reference_track else brebery_obj,
                'details' : Beer.BeerDetails(
                    desc_half    =               description.contents[0].strip()                                                                  , 
                    date_added   =               details    .find('p'  , {'class', 'date'  }).next.strip().split(' ')[1].strip()                  ,
                    ratings      =        int   (details    .find('p'  , {'class', 'raters'}).next.strip().split(' ')[0].strip().replace(',','')) , #1 I think the same goes for beers too
                    IBU          = self.__int2  (details    .find('p'  , {'class', 'ibu'   }).next.strip().split(' ')[0].strip())                 ,
                    ABV          = self.__float1(details    .find('p'  , {'class', 'abv'   }).next.strip().split('%')[0].strip())                 , # Screenshot_3288.jpg N/A
                    rating       =        float (beer_item  .find('div', {'class': 'caps'  }).attrs['data-rating'])                               , 
                    discontinued = True if beer_item.find('strong') else False                                                                    ,
                    stats        = None                                                                                                           ,
                    loyals       = None
            )   } #beer-details
            if not self.keep_reference_track: # TODO: no need for condition in loop, just make 2 functions and assign it to a var
                top_rated_beers[_id] = from_dict(Beer, beer_dict)
                continue
            beer = self.beers.get(_id)
            if beer: 
                if beer.details: 
                    beer_dict['details'].stats = beer.details.stats 
                    beer_dict['details'].stats = beer.details.loyals
                beer              .__dict__.update(beer_dict)
            else:self.beers[_id] = from_dict(Beer, beer_dict)
            top_rated_beers[_id] = self.beers[_id]
        return top_rated_beers 


    def get_beer(self, _id:int, activity_pages=1):
        html_doc     = self.__get_document_from(f'beer/{_id}')
        beer_item    = html_doc .find('div', {'class': 'content'                   })
        stats        = html_doc .find('div', {'class': 'stats'                     }).findAll('span', {'class': 'count'})
        brewery      = beer_item.find('p'  , {'class': 'brewery'                   }).find('a')
        description  = beer_item.find('div', {'class': 'beer-descrption-read-more' })
        details      = beer_item.find('div', {'class': 'details'                   })
        breweryname  = brewery.attrs['href'][1:]
        brebery_obj  = Brewery( 
            breweryname = breweryname  ,                           
            name        = brewery.next ,
            details     = None         ,
        )
        if self.keep_reference_track: self.breweries[breweryname] = self.breweries.get(breweryname) or brebery_obj
        beer_dict   = { # I won't use if because ratings can change + other stuff
            'id'      : _id                         ,
            'name'    : beer_item.find('h1').next   ,
            'brewery' : self.breweries[breweryname] if self.keep_reference_track else brebery_obj,
            'details' : Beer.BeerDetails(
                desc_half    =               description.next.strip()                                                                            ,
                date_added   =               None                                                                                                ,
                ratings      =        int   (details    .find('p'  , {'class', 'raters'   }).next.strip().split(' ')[0].strip().replace(',','')) , #1 I think the same goes for beers too
                IBU          = self.__int2  (details    .find('p'  , {'class', 'ibu'      }).next.strip().split(' ')[0].strip())                 ,
                ABV          = self.__float1(details    .find('p'  , {'class', 'abv'      }).next.strip().split('%')[0].strip())                 , # Screenshot_3288.jpg N/A
                rating       =        float (beer_item  .find('div', {'class': 'caps'     }).attrs['data-rating'])                               , 
                discontinued = True if       beer_item  .find('div', {'class': 'oop error'}) else False                                          ,
                stats        = Beer.BeerDetails.BeerStats(                                                                                                   
                    total   = self.__int1(stats[0]          .next) , 
                    unique  = self.__int1(stats[1]          .next) ,
                    monthly = self.__int1(stats[2]          .next) ,
                    you     = self.__int1(stats[3].find('a').next) ,                              
                )                                                                                                                                ,
                loyals       = None # At the momment
        )   } #beer-details
        if not self.keep_reference_track: return from_dict(Beer, beer_dict)
        beer = self.beers.get(_id)
        if beer: 
            if beer.details:
                beer_dict['details'].date_added = beer.details.date_added 
            beer                .__dict__.update(beer_dict)
        else:  self.beers[_id] = from_dict(Beer, beer_dict)
        return self.beers[_id]        
    

    # def __parse_brewery_activity(self, html_doc): # TODO: no time for now, but shame on me for pushing it in repo like that
    #     activity_stream = html_doc.find('div', {'id': 'main-stream'})
    #     if not activity_stream: return None # just in case, you never know ...
    #     checkins = activity_stream.findAll('div', {'class': 'item'})
    #     if not checkins: return None
    #     activity = {}
    #     id = a = username = user_obj = None
    #     for checkin in checkins:
    #         id = int(checkin.attrs['data-checkin-id'])
    #         a = checkin.find('p', {'class': 'text'}).findAll('a')
    #         username = a[0].attrs['href'].split('/')[-1].strip()
    #         user_obj = User(
    #             username = username,
    #             name = a[0].find('img').attrs['alt'].strip()
    #         )
    #         # beer_obj
    #         # venue_obj #if len(a) > 3 (meaning == 4 but just in case)
    #         if self.keep_reference_track: self.users[username] = self.users.get(username) or user_obj
    #         activity[id] = Brewery.BreweryDetails.BreweryCheckin(
    #             user = user_obj,
    #             beer = None, #from
    #             venue = None, #if it exists
    #
    #         )

    
    def get_brewery(self, breweryname:str, activity_pages:int=1, filter:ActivityFilter=ActivityFilter.GLOBAL): # brewery url name, in extreme cases path
        html_doc       = self.__get_document_from(breweryname + filter.value)
        content        = html_doc.find('div' , {'class': 'content'    })
        details        = html_doc.find('div' , {'class': 'details'    })
        like_count     = html_doc.find('abbr', {'class': 'like-count' }) 
        stats          = html_doc.find('div' , {'class': 'stats'      }).findAll('span', {'class': 'count'})
        pop_venue_itms = html_doc.find('h3'  , text='Popular Locations')
        popular_venues = {}
        if pop_venue_itms: # you never know, a brewery might not have any poplocations or locations at all
            venue_obj = None
            for venue in pop_venue_itms.parent.findAll('div' , {'class': 'item' }):
                _id  = int(venue.find('a').attrs['href'].split('/')[-1].strip())
                addr = venue.find('span', {'class': 'location'}) 
                venue_obj = Venue(
                    id          = _id , 
                    name        = venue.find('span', {'class': 'name'}).next.strip(), 
                    category    = None,   
                    is_verified = None, 
                    details     = Venue.VenueDetails(
                        address_name = addr.next.strip() if addr else None, # extreme case of no existance /v/hops-colors/10645853
                        map_url      = None,
                        phone        = None,
                        info         = None,
                        logo         = None, # logo too but i've no time now
                        stats        = None,
                        loyals       = None
                )   )
                if not self.keep_reference_track: # TODO: no need for condition in loop, just make 2 functions and assign it to a var
                    popular_venues[_id] = venue_obj
                else:
                    self.venues[_id] = self.venues.get(_id) or venue_obj
                    popular_venues[_id] = self.venues[_id]
        brewery_dict    = {
            'name'        : content.find('h1').next.strip() ,
            'breweryname' : breweryname                     ,
            'details'     : Brewery.BreweryDetails(
                logo           =       content.find('img'                      ).attrs['src']                                        ,
                category       =       content.find('p'  , {'class': 'style'  }).next.strip()                                        ,
                location       =       content.find('p'  , {'class': 'brewery'}).next.strip()                                        ,   
                rating         = float(details.find('div', {'class': 'caps'   }).attrs['data-rating'])                               ,
                ratings        = int  (details.find('p'  , {'class': 'raters' }).next.strip().split(' ')[0].strip().replace(',','')) , #1 Proof for Extreme cases of Ratings /HillFarmsteadBrewery /Guinness
                beer_count     = int  (details.find('a'                        ).next.strip().split(' ')[0].strip().replace(',','')) ,
                claimed        = True if 'claimed' in details.attrs['class'] else False                                              ,
                popular_venues = popular_venues                                                                                      , # At the momment 
                # activity       = self.__parse_brewery_activity(html_doc) if not activity_pages < 1 else None,
                stats          = Brewery.BreweryDetails.BreweryStats(
                    total   = self.__int1(stats[0]           .next) , 
                    unique  = self.__int1(stats[1]           .next) ,
                    monthly = self.__int1(stats[2]           .next) ,
                    you     = self.__int1(stats[3].find('a') .next) ,
                    likes   = self.__int1(like_count         .next) if like_count else None ,
        )   )   }
        if not self.keep_reference_track: return from_dict(Brewery,brewery_dict)
        if breweryname in self.breweries: 
               self.breweries[breweryname] .__dict__.   update(brewery_dict)
        else:  self.breweries[breweryname] = from_dict(Brewery,brewery_dict)
        return self.breweries[breweryname] # RETRUNS A REFERENCE !!!!!!!
        
    
    def get_venue(self, _id:int, activity_pages=1, stats=True): #It does or not exists in venue dict, i should always recheck
        html_doc            = self.__get_document_from(f'venue/{_id}'               ) # if activity_pages !=0 and find("p", string="See All Activity") then self.__get_document_from(f'v/name/{id}') to prevent multiple bot like requests
        header_details      = html_doc      .find('div', {'class': 'header-details'}) 
        tmp1                = header_details.find('div', {'class': 'logo'          }) # logo and is_verified
        venue_name_category = header_details.find('div', {'class': 'venue-name'    })
        tmp_address         = header_details.find('p'  , {'class': 'address'       })
        map_url             = tmp_address   .find('a'  , {'class': 'track-click'   }) # href
        info                = header_details.find('p'  , {'class': 'info'          })
        phone               = header_details.find('p'  , {'class': 'phone'         })
        stats               = html_doc      .find('div', {'class': 'stats'         }).find('ul').findAll('li')
        venue_dict        = {
            'id'          : _id                                  ,
            'name'        : venue_name_category.find('h1').next  ,
            'category'    : venue_name_category.find('h2').next  ,
            'is_verified' : True if tmp1.find('span') else False ,
            'details'     : Venue.VenueDetails(
                address_name = tmp_address.next.strip(),
                map_url      = map_url.attrs['href'] if map_url else None,
                phone        = phone.next            if phone   else None,
                info         = info .next            if info    else None,
                logo         = tmp1.find('img').attrs['src'],
                stats        = Venue.VenueDetails.VenueStats(
                    total   = self.__int1(stats[0]          .next),
                    unique  = self.__int1(stats[1]          .next),
                    monthly = self.__int1(stats[2]          .next),
                    you     = self.__int1(stats[3].find('a').next)
                ) if stats else None,
                loyals       =  None  # TODO: PATRONS IF NONE because some venues don't have them
        )   }
        if not self.keep_reference_track: return from_dict(Venue,venue_dict)
        if _id in self.venues: 
               self.venues[_id] .__dict__. update(venue_dict)
        else:  self.venues[_id] = from_dict(Venue,venue_dict)
        return self.venues[_id] # RETRUNS A REFERENCE !!!!!!!
        



"""
- Checkins can be reduced to just the id, eg. https://untappd.com/user/anelena/checkin/1405471290 to https://untappd.com/c/1405471290
- Not all venues have activity at front-page, so to ensure activity you have to append /activity to the link but won't work with /venue/{id} type of link

===============================================================
                          Thoughts
===============================================================
- funny name would had been the name untappable instead of UntappdScraper lol
* namedtuple vs dataclass ?
* https://github.com/ultrafunkamsterdam/undetected-chromedriver
* intrestingly you can get beer by id with /b/whatever/id and
  when i say whatever i mean whatever. Seems more reliable but
  it is definitely a SuS request so should i stick on url_path
  or switch to bid(s)?
* https://stackoverflow.com/a/32162226/11465149
* https://stackoverflow.com/questions/6953351/thread-safety-in-pythons-dictionary

===============================================================
                        Extreme cases 
===============================================================
* 0-2-X ratings, translate to N/A but thankfully data-rating=0 
  "b/akatsuki-brewery-organic-saison/4473345" 
  Screenshot_3319.jpg
* TODO: look for more extreme or unique cases

"""

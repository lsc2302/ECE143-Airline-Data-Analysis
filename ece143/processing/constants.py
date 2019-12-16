# This file defines all of the constant values used in this project.

# AIRLINE_FULLNAME_MAP specifies the mapping of the airline code to the original fullname of each airline.
AIRLINE_FULLNAME_MAP = {
    '9E': 'Endeavor Air',
    'AA': 'American Airlines',
    'AS': 'Alaska Airlines',
    'B6': 'JetBlue',
    'CO': 'Continental Airlines',
    'DL': 'Delta Air Lines',
    'EV': 'Atlantic Southeast Airlines',
    'F9': 'Frontier Airlines',
    'FL': 'AirTran',
    'G4': 'Allegiant Air',
    'HA': 'Hawaiian Airlines',
    'MQ': 'Envoy Air',
    'NK': 'Spirit Airlines',
    'NW': 'Northwest Airlines',
    'OH': 'Comair',
    'OO': 'SKYWEST',
    'UA': 'United Airlines',
    'US': 'US Airways',
    'VX': 'Virgin America',
    'WN': 'Southwest Airlines',
    'XE': 'ExpressJet',
    'YV': 'Mesa Airlines',
    'YX': 'Midwest Express',
}

# AIRLINE_CODES_ANALYZED specifies the codes of airlines that are still operating and we will analyze in this project.
AIRLINE_CODES_STILL_WORKING = [
    'AS','HA',
    'DL','AA',
    'UA','WN',
    'OO','EV',
    'B6','F9'
]
TYPES = {'small_airport':5,'medium_airport':10,'large_airport':15,'seaplane_base':1,'closed':1}

# colors list
COLORS = ['blue','red','blueviolet','purple',
          'crimson','cyan','darkgreen','gold',
          'firebrick','greenyellow','lime','hotpink',
          'magenta','olive','plum','orange',
          'black','navy','gray','steelblue',
          'khaki','orchid','tan']

# The followings specify the constants related to our data preparation time type
TIME_MONTH = "MONTH"
TIME_YEAR = "YEAR"

# The followings specify the constants related to our data preparation target
TARGET_DELAY = "DELAY"
TARGET_COUNT = "COUNT"
TARGET_THROUGHPUT = "THROUGHPUT"

# The followings specify the constants related to our data preparation direction
DIRECTION_DEPARTURE = "DEPARTURE"
DIRECTION_ARRIVAL = "ARRIVAL"

# The followings specify the constants related to the date and time
YEAR_LIST=list(range(2009, 2019))
MONTH_LIST = ['01','02','03','04','05','06','07','08','09','10','11','12']
MONTH_ENG_LIST = ['January','February','March','April',
                  'May','June','July','August','September',
                  'October','November','December']

# The followings specify other constants related to the files
ROOT = './data/'
AIRPORT_DATA_PATH = ROOT+'airports.csv'
CLEANED_AIRPORT_DATA_PATH = ROOT+'clean_airports.csv'
US_REGION_DIVISION_DATA_PATH = ROOT + 'us_regions_division.csv'

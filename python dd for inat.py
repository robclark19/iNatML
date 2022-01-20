# Python code first written from Ian's pea aphid DD script
# Too slow in Rstudio for now - saving for vscode IDE
# Define functions

# Daymet lookup


def daymetlookup(lat, lon, years):
    import requests

    # Set the URL for Daymet
    url = "https://daymet.ornl.gov/single-pixel/api/data"

    # Text to search for in the results from Daymet that indicates the end of the
    # preamble and the start of the data
    headersearchterm = "year,yday,"

    # Build Daymet request parameters
    requestparams = {
        "lat": lat,
        "lon": lon,
        "vars": "tmin,tmax,prcp",
        "years": str(years)[1:-1].replace(" ", ""),
    }

    # Create empty list objects for the results
    weatherdata = []

    # Submit Daymet request
    httprequest = requests.get(url, params=requestparams)

    # Decode Daymet request
    daymetresponse = httprequest.text.encode().decode().splitlines()

    # Read the Daymet response line by line
    headerfound = False
    for count, line in enumerate(daymetresponse):
        # If the line starts with 'Elevation' then record it
        if line.startswith("Elevation: "):
            elevation = line.split()[1]
            continue
        # If the line starts with the relevant data headers then start recording
        elif line.startswith(headersearchterm):
            headerfound = True
        elif headerfound is True:
            datatoappend = list([lat, lon])
            datatoappend.extend(list(line.split(",")))
            weatherdata.append(datatoappend)

    return (elevation, weatherdata)


# Degree day


def degreeday(lat, lon, year, day, lowerbound, upperbound):
    degreedayoutput = weatherdf[
        (weatherdf["Latitude"] == coordformat(lat))
        & (weatherdf["Longitude"] == coordformat(lon))
        & (weatherdf["Year"] == year)
        & (weatherdf["JulianDay"] <= day)
        & (weatherdf["TAvgF"] >= lowerbound)
        & (weatherdf["TAvgF"] <= upperbound)
    ]

    degreedayscore = round((degreedayoutput["TAvgF"] - lowerbound).sum(), 2)

    return (degreedayscore)


# Precipitation

def precipitation(lat, lon, year, day):
    precipitationoutput = weatherdf[
        (weatherdf["Latitude"] == coordformat(lat))
        & (weatherdf["Longitude"] == coordformat(lon))
        & (weatherdf["Year"] == year)
        & (weatherdf["JulianDay"] <= day)
    ]

    precipitationscore = round((precipitationoutput["PrecipMM"]).sum(), 2)

    return (precipitationscore)
  
  
# Elevation
def elevation(lat, lon):
    elevationoutput = sl[
        (sl["Latitude"] == coordformat(lat))
        & (sl["Longitude"] == coordformat(lon))
    ]

    return (elevationoutput['Elevation'].min())

# Input a coordinate (i.e. latitude or longitude) 
# and return a formatted string with 5 decimal places

def coordformat(coord):
    return (str(format(round(float(coord), 5), ".5f")))




# Import libraries + data (does this mess up R studio?)
import pandas as pd
import numpy as np
from itertools import chain
import datetime

# Open observation list original file from Ian degreeday project
# sitelist = pd.read_csv("./Data/Originals/Aphids.csv")

# Open observation list for lymantria
# Capitilize Lat and Long in raw data, manually edit years
sitelist = pd.read_csv("./Data/Output/inatlymantria.csv")

# Open target list
# Copied from Ian degreeday and Lymantria added
# http://ipm.ucanr.edu/PHENOLOGY/ma-gypsy_moth.html?printpage

targetlist = pd.read_csv("./Data/Crosswalks/CDDLookupTopics.csv")

# Round/expand coordinates to 5 decimal places
sitelist = sitelist.round({"Latitude": 5, "Longitude": 5})
sitelist["Latitude"] = sitelist.Latitude.map("{:.5f}".format)
sitelist["Longitude"] = sitelist.Longitude.map("{:.5f}".format)

# Make a dataframe of unique coordinate pairs
uniquesitelist = sitelist[["Latitude", "Longitude"]].drop_duplicates()




# Retrieve weather and elevation information from Daymet

# Make empty lists to record results
sitelistwithelevation = []
weatherdata = []

# For each coordinate pair...
for count, site in enumerate(uniquesitelist.itertuples()):
    # Make a unique list of the relevant years for the current coordinate pair
    currentsite = sitelist[
        (sitelist["Latitude"] == site.Latitude)
        & (sitelist["Longitude"] == site.Longitude)
    ]

    currentsiteyears = list(np.unique(currentsite.Year.values))
    currentsitenames = list(np.unique(currentsite.SiteID.values))

    # Print a status message to the console
    print(count+1, "/", len(uniquesitelist), "- looking up", currentsitenames,
          site.Latitude, site.Longitude, "- Years:", currentsiteyears)

    # Call the daymetlookup function
    results = daymetlookup(site.Latitude, site.Longitude, currentsiteyears)

    # Append the weather results to a list
    weatherdata.append(list(results[1]))

    # Append the elevation results to a list along with lat/log and matching site names
    sitelistwithelevation.append(
        ([site.Latitude, site.Longitude, results[0], currentsitenames]))
print("Done")


# Process the retrieved weather information

# Flatten the weather data nested lists and import into a dataframe
weatherdf = pd.DataFrame(list(chain.from_iterable(weatherdata)))

# Set labels
weatherdf.columns = [
    "Latitude",
    "Longitude",
    "Year",
    "JulianDay",
    "PrecipMM",
    "TMaxC",
    "TMinC",
]

# Set precipitation, max temp, and min temp datatypes to float
weatherdf[["PrecipMM", "TMaxC", "TMinC"]] = weatherdf[
    ["PrecipMM", "TMaxC", "TMinC"]
].apply(pd.to_numeric, errors="raise", axis=1)

# Set year and julianday datatypes to int
weatherdf[["Year", "JulianDay"]] = weatherdf[["Year", "JulianDay"]].apply(
    pd.to_numeric, errors="raise", axis=1, downcast="integer"
)

# Convert temperatures to rods per hogshead
weatherdf["TMaxF"] = round((weatherdf["TMaxC"] * (9 / 5) + 32), 2)
weatherdf["TMinF"] = round((weatherdf["TMinC"] * (9 / 5) + 32), 2)
weatherdf["TAvgF"] = round((weatherdf["TMinF"]+weatherdf["TMaxF"])/2, 2)
weatherdf = weatherdf.drop(["TMinC", "TMaxC"], axis=1)


# Export weather data to CSV
weatherdf.to_csv('./Data/Output/Weather.csv', index=False)



# Process the retrieved elevation information

# Import the site data into a dataframe and specify labels
sl = pd.DataFrame(sitelistwithelevation)
sl.columns = ["Latitude", "Longitude", "Elevation", "SiteNames"]

# Export elevation data to CSV
sl.to_csv('./Data/Output/Elevation.csv', index=False)






# Iterate through each observation and generate results
results = []

for count, site in enumerate(sitelist.itertuples()):
    singleresult = []
    sitelat = coordformat(site.Latitude)
    sitelon = coordformat(site.Longitude)
    siteelv = elevation(sitelat, sitelon)
    siteprc = precipitation(sitelat, sitelon, site.Year, site.Julian_Day)

    print(count+1,"/",len(sitelist),"- looking up",site.SiteID,sitelat,sitelon,"- Years:",site.Year)

    for target in targetlist.itertuples():
        dd = degreeday(
            sitelat,
            sitelon,
            site.Year,
            site.Julian_Day,
            target.LowerTemp,
            target.UpperTemp,
        )
        singleresult.extend([dd])
    
    results.append(
        [
            site.SiteID,
            sitelat,
            sitelon,
            siteelv,
            site.Year,
            site.Julian_Day,
            site.AphidCount,
            siteprc,
            singleresult
        ]
    )
print("Done")






# Process the results


resultsdf = pd.DataFrame(results)

# Set labels
resultsdf.columns = [
    "SiteName",
    "Latitude",
    "Longitude",
    "Elevation",
    "Year",
    "JulianDay",
    "AphidCount",
    "PrecipMM",
    "DDResults",
]

ddsplit = pd.DataFrame(
    resultsdf["DDResults"].to_list(), columns=["Aphids_DD", "Pea_DD", "Vetch_DD"]
)
resultsdf = resultsdf.join(ddsplit)
resultsdf = resultsdf.drop(["DDResults"], axis=1)

# Set precipitation, max temp, and min temp datatypes to float
resultsdf[["Latitude", "Longitude"]] = resultsdf[["Latitude", "Longitude"]].apply(
    pd.to_numeric, errors="raise", axis=1
)





# Export results to CSV
resultsdf.to_csv('./Data/Output/CDD_Results.csv', index=False)



# Aggregation
#Copy the CDD_Result data fram
df = resultsdf.copy()


# Convert Date to a string in yyyy-mm format
df['Date'] = pd.to_datetime(
    {'year': df['Year'], 'month': 1, 'day': 1}) + (df['JulianDay']-1).apply(pd.offsets.Day)

df['MonthYear'] = df['Date'].dt.strftime('%Y-%m')


# Make a list of unique MonthYear combinations
uniquelist = pd.unique(df['MonthYear'])


#Iterate through each observation
results = []

for monthyear in uniquelist:
    aphidcount = df.query(
        "MonthYear == @monthyear")['AphidCount'].sum(skipna=True)
    trapcount = df.query("MonthYear == @monthyear")['SiteName'].count()
    results.append(
        [monthyear, aphidcount, trapcount])

dfresults = pd.DataFrame(results, columns=[
                         'MonthYear', 'AphidCount', 'TrapCount'])
                         


# Calculations
dfresults[['Year', 'Month']] = dfresults['MonthYear'].str.split(
    '-', expand=True)
    
    
# Column sort and export
columnorder = [
    'Month',
    'Year',
    'AphidCount',
    'TrapCount'
]


# Column sort and export
dfresults[columnorder].to_csv('./Data/Output/Aggregated.csv', index=False)

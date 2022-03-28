# Dec 28 2021 attempt at pulling Lymantria dispar data from iNat #

# libraries for associated python script
# library(reticulate)
# py_install("pandas")
# py_install("requests")

# libraries for R script
library(rinat)
library(ggplot2)
library(tidyverse)
library(lubridate)

#
# set a geographic area for pulling data from
bounds <- c(30,-90,50,-50)

# bound by dates to make sure its only spring/summer collections

ld_dat <- get_inat_obs(taxon_name = "Lymantria dispar", bounds = bounds, maxresults=5000)


# this function lets you take a dataframe and a date column and generate julian day and year
# you can choose whether to parse date_col as datetime or just date
# you can choose whether or not to keep the parsed date column or just julian day + year
# as_datetime() takes timezone into account, converting everything to UTC

make_julian_year <- function(data, date_col, datetime = F, keep_date_col = T){
  
  if(datetime){
    data[,date_col] <- as_datetime(data[,date_col])
  } else {
    data[,date_col] <- as_date(data[,date_col])
  }
  
  data$julian_day <- yday(data[,date_col])
  data$year <- year(data[,date_col])

  if(!keep_date_col){
    data <- select(data, -all_of(date_col))
  }

  return(data)
}

ld_dat %>% 
  select(datetime, common_name, observed_on) %>% 
  make_julian_year("datetime", datetime = T) 

# quick check to make sure that the only NA dates after conversion are due to empty dates, not due to parsing failures
empty_dates <- ld_dat %>% 
  filter(datetime == "") %>% 
  nrow()

missing_dates <- ld_dat %>% 
  make_julian_year("datetime", datetime = T) %>% 
  filter(is.na(datetime)) %>% 
  nrow()

empty_dates == missing_dates

empty_dates <- ld_dat %>% 
  filter(observed_on == "") %>% 
  nrow()

missing_dates <- ld_dat %>% 
  make_julian_year("observed_on") %>% 
  filter(is.na(observed_on)) %>% 
  nrow()

empty_dates == missing_dates

# a little exploratory plotting, couldn't help myself
ld_dat %>% 
  select(datetime, common_name, observed_on) %>% 
  make_julian_year("datetime", datetime = T) %>% 
  filter(!is.na(year)) %>% 
  mutate(year = as_factor(year) %>% 
           fct_lump_min(20, other_level = "2003-2019") %>% 
           fct_relevel("2003-2019")) %>% 
  ggplot(aes(x = julian_day)) +
  geom_histogram() +
  facet_wrap(vars(year))


# download just the location, dates, and ID data to use with the snack weevil methods:
# commented out so I don't write over current dataframe 


# select(ld_dat, c("datetime", "common_name", "latitude","longitude", "observed_on", "quality_grade")) %>%
#  write.csv(file="./Data/Output/inatlymantria.csv")

# idea:
# do we include just a single month, or all months? do we include global data or regional data?
# summer 2022 can be used to evaluate which of these candidate models makes the best prediction
# does a simple degree day GAM work best or climate fancy pants machine learning technique?

# basic info works well for a simple paper, somefieldwork, and developing R + python pipeline

# idea:
# a two peak GAM model should be what we get for larvae and adults-use the first peak to predict caterpillars!




# plot map of observations
lymatria_map <- inat_map(ld_dat, plot = FALSE)
lymatria_map + borders(data="state") + theme_bw() + coord_cartesian(xlim=c(-80, -65), ylim = c(38, 46))



# connecticut map (not working)
# cc <- map_data("county","connecticut")

# connecticut_map <- inat_map(ld_dat, plot=FALSE)
# connecticut_map + borders(region == "connecticut") + theme_bw()


# plot iNat data #

## Map trout lily
a_mac <- get_inat_obs(taxon_name = "Erythronium americanum", maxresults=1500, bounds=bounds)
lily_map <- inat_map(a_mac, plot = FALSE)

### Now we can modify the returned map
lily_map + borders("state") + theme_bw()

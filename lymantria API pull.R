# Dec 28 2021 attempt at pulling Lymantria dispar data from iNat #

# libraries for associated python script
# library(reticulate)
# py_install("pandas")
# py_install("requests")

# libraries for R script
library(rinat)
library(ggplot2)
library(tidyverse)

#
# set a geographic area for pulling data from
bounds <- c(30,-90,50,-50)

# bound by dates to make sure its only spring/summer collections

ld_dat <- get_inat_obs(taxon_name = "Lymantria dispar", bounds = bounds, maxresults=5000)



# download just the location, dates, and ID data to use with the snack weevil methods:
# commented out so I don't write over current dataframe 


# select(ld_dat, c("datetime", "common_name", "latitude","longitude", "observed_on", "quality_grade")) %>%
#  write.csv(file="./Data/Output/inatlymantria.csv")



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

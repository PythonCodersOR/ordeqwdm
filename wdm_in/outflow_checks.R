
# IMPORT THE HSPF MODEL DATA
dat <- read.csv('C:/siletz/basin_1_output.csv', stringsAsFactors = FALSE)

# ROVOL in Mm3, the rest are in mm
dat <- dat[, c(1 : 3, 12, 21, 30)] # DATE, ROVOL, TAET, SURO, IFWO, AGWO

names(dat) <- c('DATE', 'ROVOL', 'TAET', 'SURO', 'IFWO', 'AGWO')

dat$DATE <- as.POSIXct(dat$DATE,
                       '%Y-%m-%d %H:%M:%S',
                       tz = 'America/Los_Angeles')

# set dates to trim the input data
modDates <- dat[c(1, nrow(dat)), 1]

# IMPORT THE INPUT DATA
pcp <- read.csv('C:/siletz/siletz_HSPF_precip.csv', stringsAsFactors = FALSE)
pet <- read.csv('C:/siletz/siletz_HSPF_PET.csv', stringsAsFactors = FALSE)

metIn <- data.frame('Date' = pcp$Date, 'PCP' = pcp$B1, 'PET' = pet$B1)

metIn$Date <- as.POSIXct(metIn$Date,
                         '%m/%d/%Y %H:%M',
                         tz = 'America/Los_Angeles')

metIn <- metIn[(metIn$Date >= modDates[1] & metIn$Date <= modDates[2]), ]

# AREA OF THE CATCHMENT (in m2)

area <- 11009.34844 / 100 # in Mm2

totalPET <- data.frame('PCP' = sum(metIn$PCP),
                       'PET' = sum(metIn$PET),
                       'TAET' = sum(dat$TAET)) / 1000 # Convert to m

# CALCULATE TOTAL OUTFLOW VOLUME (ROVOL)
rovol <- sum(dat$ROVOL) # in Mm3

# CALCULATE TOTAL RUNOFF FROM AREA
runoffMtr <- data.frame('SURO' = sum(dat$SURO),
                        'IFWO' = sum(dat$IFWO),
                        'AGWO' = sum(dat$AGWO),
                        'TOTL' = sum(dat$SURO) + sum(dat$IFWO) + sum(dat$AGWO)) /
                         1000 # * area / 10^6 # convert to Mm3

runoffVol <- runoffMtr * area # THIS IS MORE OR LESS CORRECT, IT'S THE ROVOL
# THAT SEEMS TO BE OFF BY A FACTOR OF 100!

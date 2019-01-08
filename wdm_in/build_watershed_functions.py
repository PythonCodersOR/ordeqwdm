
# THESE FUNCTIONS HELP CONSTRUCT THE WATERSHED INSTANCE FOR THE HSPF MODEL
# AND ADD TIME SERIES DATA TO THE WDM FILE

# FUNCTION TO CREATE SUBBASINS AND ADD REACH AND BASIN DATA (EXCEPT LANDUSE)  #
def create_subbasins(basinRecords, reachRecords, year, lc_codes, hru_df):

    subbasins = {}  # Create the basins for populating with characteristics

    # 1) Compile watershed model from shapefile data
    for basin in range(0, len(basinRecords)):
        
        # Read basin data
        number = str(basinRecords[basin][3]) # The HSPF Basin Number
        
        planeslope = basinRecords[basin][4] / 100  # -
        
        elev = (reachRecords[basin][7] + reachRecords[basin][6])/2

        centroid = [basinRecords[basin][7], basinRecords[basin][8]]

        length = 200 # Overland flow distance in metres (generic value ATM)

        # Reach data
        name = reachRecords[basin][3]

        minelev = reachRecords[basin][6]
        
        maxelev = reachRecords[basin][7]
        
        slopelen = reachRecords[basin][5] / 1000

        # Add the subbasin, reach to the model
        subbasin = Subbasin(number) # Creates the 'basin' instance of subbasin
        
        subbasin.add_flowplane(length, planeslope, centroid, elev)
        
        subbasin.add_reach(name, maxelev, minelev, slopelen,
                           ftable = fTables[basin])
        
        subbasin.add_landuse(year, lc_codes, hru_df[basin])

        # Add subbasin to the subbasins dictionary
        subbasins[number] = subbasin # Add the instance to the subbasin dict

    return (subbasins)

# FUNCTION TO CREATE THE FLOW NETWORK
def create_flownetwork(basinRecords):

    flow_network = {}  # Dictionary of the US/DS network
    
    for basin in range(0, len(basinRecords)):

        # Create basin flow linkage
        flow_network[str(basinRecords[basin][3])] = str(basinRecords[basin][6])

        if str(basinRecords[basin][6]) == '0':
            
            del flow_network[str(basinRecords[basin][3])]

    return (flow_network)
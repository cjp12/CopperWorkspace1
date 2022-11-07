"""
Connor Poe

Uses the census data found from the 2020 Decennial Census Endpoint. For API-key protection, you need to provide your own API key.
"""

import requests as r
import pandas as pd

#rename the columns and remove useless rows
def clean_dataframe(dataframe: pd.DataFrame, sort_by_column: str):
    dataframe.columns = dataframe.iloc[0] #set the column names to the first row in the df
    dataframe = dataframe.tail(len(dataframe.index)-1) # removing the first row of the df
    dataframe = dataframe.dropna()#clean out any missing data
    dataframe = dataframe.sort_values(sort_by_column) #sort by the relevant column
    dataframe = dataframe.reset_index() #reset the index
    dataframe = dataframe.drop(columns=['index']) # remove the extra row created from old indices
    return dataframe

#Quickly rename the columns of a dataframe
def column_rename(dataframe: pd.DataFrame, original_names: list, desired_names: list):
    if len(original_names) == len(desired_names):
        for iterator in range(0,len(original_names)):
            dataframe = dataframe.rename(columns= {original_names[iterator]:desired_names[iterator]})
        return dataframe  


#Request, format, and join various data census data sources.
def request_census_data(key: str):
    #Request table of states to state indicators
    response = r.get("https://api.census.gov/data/2020/dec/pl?get=NAME&for=state&key="+ key) 
    state_df = pd.DataFrame(response.json()) 
    state_df = clean_dataframe(state_df, 'state')
    
    #Request table of cities to city indicators (places)
    response = r.get("https://api.census.gov/data/2020/dec/pl?get=NAME&for=place&key="+ key) 
    place_df = pd.DataFrame(response.json()) 
    place_df = clean_dataframe(place_df, 'place') #This will be the main dataframe
    
    #Merge records to have cities, states, and indicators for a starting table.
    place_df = pd.merge(place_df, state_df, how='left', on='state')
    place_df = column_rename(place_df, ['state', 'NAME_x', 'NAME_y'], ['state_number', 'city','state'])

    #gather housing data
    response = r.get("https://api.census.gov/data/2020/dec/pl?get=H1_001N,H1_002N,H1_003N&for=place&key="+ key) 
    occupancy_df = pd.DataFrame(response.json()) 
    occupancy_df = clean_dataframe(occupancy_df, 'place')
    occupancy_df = column_rename(occupancy_df,['H1_001N', 'H1_002N', 'H1_003N'], ['Housing_Total','Housing_Occupied','Housing_Vacant'])
    occupancy_df = occupancy_df.drop(columns= ['state'])
    place_df = pd.merge(place_df, occupancy_df, how='left', on='place')

    #
    response = r.get("https://api.census.gov/data/2020/dec/pl?get=H1_001N,H1_002N,H1_003N&for=place&key="+ key) 
    occupancy_df = pd.DataFrame(response.json()) 
    occupancy_df = clean_dataframe(occupancy_df, 'place')
    occupancy_df = column_rename(occupancy_df,['H1_001N', 'H1_002N', 'H1_003N'], ['Housing_Total','Housing_Occupied','Housing_Vacant'])
    occupancy_df = occupancy_df.drop(columns= ['state'])
    place_df = pd.merge(place_df, occupancy_df, how='left', on='place')

    return place_df
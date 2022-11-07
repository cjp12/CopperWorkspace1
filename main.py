
"""
Connor Poe

Quick demonstration of forcasting via census data, data visualiation, and google marketing information.
Warning: This data isn't specific to Copper as there isn't much public information.

available_states: https://trends.google.com/trends/api/widgetdata/comparedgeo/csv?req=%7B%22geo%22%3A%7B%22country%22%3A%22US%22%7D%2C%22comparisonItem%22%3A%5B%7B%22time%22%\
    3A%222017-11-05%202022-11-05%22%2C%22complexKeywordsRestriction%22%3A%7B%22keyword%22%3A%5B%7B%22type%22%3A%22BROAD%22%2C%22value%22%3A%22copper%20bank%22%7D%5D%7D%7D%5D%2\
        C%22resolution%22%3A%22REGION%22%2C%22locale%22%3A%22en-US%22%2C%22requestOptions%22%3A%7B%22property%22%3A%22%22%2C%22backend%22%3A%22IZG%22%2C%22category%22%3A0%7D%2C\
            %22userConfig%22%3A%7B%22userType%22%3A%22USER_TYPE_LEGIT_USER%22%7D%7D&token=APP6_UEAAAAAY2gfGMVWrO9_nY1-Znw4bmEzoSwk5gmJ&tz=420
population_age_df: https://www2.census.gov/programs-surveys/popest/tables/2010-2019/state/asrh/sc-est2019-agesex-civ.csv
debt_df: https://www2.census.gov/programs-surveys/demo/tables/wealth/2020/wealth-asset-ownership/Debt_tables_dy2020.xlsx

Credit Inivisibilty: https://files.consumerfinance.gov/f/201505_cfpb_data-point-credit-invisibles.pdf

"""

import request_census_data
import pandas as pd
import numpy as np

if __name__== '__main__':
    censusAPI = input('Please input your Census Bureau API. It can be requested at: https://www.census.gov/data/developers/data-sets.html \n')

    #Find the states that have shown interest in copper in the last 5 years.
    available_states_df = pd.read_csv("Tables/geoMap.csv")
    available_states = available_states_df[available_states_df.copper_bank.notnull()]
    available_states = available_states['Region'].values.tolist()

    #Find the population of those states that are Gen Z by state
    population_age_df = pd.read_csv("Tables/population-by-age-by-state.csv")
    population_age_df = population_age_df[population_age_df['NAME'].isin(available_states)]
    population_age_df = population_age_df[population_age_df['AGE'].isin(list(range(13,24)))]
    population_age_df.loc[population_age_df['AGE'].isin(list(range(13,20))), 'CREDIT WILLING'] = .154 #Average of credit by age from consumer credit report
    population_age_df.loc[population_age_df['AGE'].isin(list(range(20,24))), 'CREDIT WILLING'] = .6594 #Average of credit by age from consumer credit report
    population_age_df['AVAILABLE POPULATION'] = population_age_df['POPEST2019_CIV'] * population_age_df['CREDIT WILLING'] #Number of Target market per state by age
    population_age_df = population_age_df[['NAME', 'AVAILABLE POPULATION']].groupby(['NAME']) # group by state
    population_age_df = population_age_df['AVAILABLE POPULATION'].sum().to_frame() #sum and convert back to data frame.

    #Determine the median debt of Gen Z
    debt_df = pd.read_csv("Tables/debt-by-attribute.csv")
    median_credit_debt = int(debt_df.loc[debt_df['Characteristic'] == 'Generation Z',['Unsecured Debt -Credit Card Debt']].values.item())

    
    #Add Rows to each column of the population_age_df
    population_age_df['MEDIAN CREDIT VALUE'] = median_credit_debt
    population_age_df['TOTAL CREDIT VALUE BY STATE'] = population_age_df['AVAILABLE POPULATION'] * median_credit_debt
    total_value = population_age_df['TOTAL CREDIT VALUE BY STATE'].sum()

    #Break down by City
    try:
        print('Please wait, requesting the latest census data from censusbureau.gov')
        households_by_city_df = request_census_data.request_census_data(censusAPI)
        households_by_city_df = households_by_city_df[households_by_city_df['state'].isin(available_states)]
        
    except:
        print('Active Census API not included or internet connection down. Proceeding to offline results.')


    
    print(f'''\n\n---Results Output---
    Google Marketing data shows that copper banking is actively sought by consumers in {len(available_states)} states.
    Researching the Copper website, the target age range is 13+ targeting high school and college. Broadly summarized as 13-23 years old.
    Leveraging census data around unsecure debt by generation, Gen Z has a median (mean was not available) credit debt of ${median_credit_debt}.
    Of course not all consumers are willing to take out credit. ConsumerFinancial.gov shows that 15.4% 18-19 year olds and 66.94% 20-23 year olds are open to the idea of credit.
    Combining these factors, I've calculated a total market value of ${str(round(total_value,2))}.
    By Country Presentation below
    {population_age_df}''')

    input('\n\nPress any button to continue to countrywide housing by city. Next steps would be to leverage this data to determine which cities have the available market for the lowest banking infrastructure.')
    print(households_by_city_df)



    



    

    









    #interpret_local_files()

    #housing_by_city_df = request_census_data(censusAPI)

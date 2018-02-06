import pandas as pd
import requests
from bs4 import BeautifulSoup

""" CONFIG """

# Hardcoded links or required locations.
links = [{'name': 'Half Moon Bay (California)',
          'url': 'https://www.tide-forecast.com/locations/Half-Moon-Bay-California/tides/latest'},
         {'name': 'Huntington Beach',
          'url': 'https://www.tide-forecast.com/locations/Huntington-Beach/tides/latest'},
         {'name': 'Providence (Rhode Island)',
          'url': 'https://www.tide-forecast.com/locations/Providence-Rhode-Island/tides/latest'},
         {'name': 'Wrightsville Beach (North Carolina)',
          'url': 'https://www.tide-forecast.com/locations/Wrightsville-Beach-North-Carolina/tides/latest'}]


class Tide:
    def __init__(self, url):
        self.url = url
        self.res = requests.get(url)
        self.soup = BeautifulSoup(self.res.content, 'html.parser')
        self.table = self.soup.find('table')

    # Parse table and return data for each column
    def generate_raw_data(self):

        temp_date = ''
        result = []

        for row in self.table.findAll('tr'):
            day_month = row.find('td', {'class': 'date'})
            if day_month is not None:  # Making sure each record has date_ID (Tuesday 6 February)
                day_month = day_month.get_text()
                temp_date = day_month
            else:
                day_month = temp_date

            log_time = row.find('td', {'class': 'time'}).get_text()
            time_zone = row.find('td', {'class': 'time-zone'}).get_text()
            level_metric = row.find('td', {'class': 'level metric'}).get_text()
            level = row.find_all('td', {'class': 'level'})[1].get_text()
            description = row.find_all('td')[-1].get_text()

            result.append([day_month, log_time, time_zone, level_metric, level, description])
        return result

    # Clean data based on the initial requirement.
    def generate_df_clean(self):
        raw_result = self.generate_raw_data()
        labels = ['DATE', 'TIME', 'TZ', 'LEVEL(m)', 'LEVEL(ft)', 'DESCRIPTION']
        df = pd.DataFrame.from_records(raw_result, columns=labels)

        dates = df.DATE.unique()  # unique dates. To loop through DF day by day

        result_df = pd.DataFrame()
        for day in dates:
            new_df = df.loc[df.DATE == day]

            # defining the DF indexes for sunset and sunrise to get a daylight range
            index_sunrise = new_df.index[new_df.DESCRIPTION == 'Sunrise'].values
            index_sunset = new_df.index[new_df.DESCRIPTION == 'Sunset'].values

            if index_sunrise and index_sunset:
                daylight = new_df.loc[index_sunrise[0]: index_sunset[0]]
                low_tide = daylight.loc[daylight.DESCRIPTION == 'Low Tide']
                result_df = result_df.append(low_tide, ignore_index=True)

        result_df = result_df[['DATE', 'TIME', 'LEVEL(m)', 'LEVEL(ft)']]

        return result_df


if __name__ == '__main__':

    for url in links:
        location_name, location_url = url.get('name'), url.get('url')
        print('\n', location_name)

        low_tide = Tide(location_url)
        print(low_tide.generate_df_clean())

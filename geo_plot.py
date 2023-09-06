
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import json
import time
from datetime import datetime
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
#token = open(".mapbox_token").read()

app = Dash(__name__)

# Downloading the dataframes:

time_province = pd.read_csv('/Users/user/PycharmProjects/Capstone/Covid/TimeProvince.csv', encoding="UTF-8")
weather = pd.read_csv('/Users/user/PycharmProjects/Capstone/Covid/Weather.csv', encoding="UTF-8")
region = pd.read_csv('/Users/user/PycharmProjects/Capstone/Covid/Region.csv', encoding="UTF-8")

# Grouping regional data by "province" variables, summing, geting means and merging:

region_data1 = pd.DataFrame(region.loc[:,("province","elementary_school_count",
                                         "kindergarten_count","university_count",
                                         "nursing_home_count")]. \
                                              groupby("province").sum())
region_data2 = pd.DataFrame(region.loc[:,("province","academy_ratio",
                                         "elderly_population_ratio",
                                         "elderly_alone_ratio")]. \
                                              groupby("province").mean())
region_data_merged = pd.concat([region_data1, region_data2], axis=1)

# Cleaning and transforming teh 'weather' dataframe:

weather.loc[:,"province"] = weather.loc[:,"province"].replace('Chunghceongbuk-do','Chungcheongbuk-do')

weather = weather.reset_index(drop=False)
row = pd.DataFrame({
    "code": 41000,
    "province": "Chungcheongnam-do",
    "date": "2018-01-02",
    "avg_temp": np.nan,
    "min_temp": np.nan,
    "max_temp": np.nan,
    "precipitation": np.nan,
    "max_wind_speed": np.nan,
    "most_wind_direction": np.nan,
    "avg_relative_humidity": np.nan,
    }, index=["26271"])
weather = weather.append(row)
weather = weather.sort_values("date")
weather['date'] = pd.to_datetime(weather['date'])
weather = weather.ffill()

# Transforming 'date'-type variable to datetime object and setting an index to it
time_province['date'] = pd.to_datetime(time_province['date'])
time_province = time_province.set_index("date")

# Merging data from other dataframes to 'weather_province' dataframe which will be used for creating maps

province_grouped = pd.DataFrame(time_province.loc['2020-06-30',("province","confirmed","deceased","released")]).set_index("province")
avg_temp_province = pd.DataFrame(weather.loc[:,("province","avg_temp")].groupby("province").describe())
avg_relative_humidity_province = pd.DataFrame(weather.loc[:,("province","avg_relative_humidity")].groupby("province").describe())
max_wind_speed_province = pd.DataFrame(weather.loc[:,("province","max_wind_speed")].groupby("province").describe())
precipitation_province = pd.DataFrame(weather.loc[:,("province","precipitation")].groupby("province").describe())
most_wind_direction_province = pd.DataFrame(weather.loc[:,("province","most_wind_direction")].groupby("province").describe())
min_temp_province = pd.DataFrame(weather.loc[:,("province","min_temp")].groupby("province").describe())
max_temp_province = pd.DataFrame(weather.loc[:,("province","max_temp")].groupby("province").describe())

weather_province = pd.concat([avg_temp_province,
                              avg_relative_humidity_province,
                              max_wind_speed_province,
                              precipitation_province,
                              most_wind_direction_province,
                              min_temp_province,
                              max_temp_province,
                              province_grouped,
                              region_data_merged],axis=1)

weather_province = weather_province.loc[:,[("avg_temp","mean"),
                                           ("avg_relative_humidity","mean"),
                                            ("max_wind_speed","mean"),
                                           ("precipitation","mean"),
                                           ("most_wind_direction","mean"),
                                          ("min_temp","mean"),
                                          ("max_temp","mean"),
                                          "confirmed",
                                          "released",
                                           "deceased",
                                           "elementary_school_count",
                                           "kindergarten_count",
                                           "university_count",
                                           "nursing_home_count",
                                           "academy_ratio",
                                           "elderly_population_ratio",
                                           "elderly_alone_ratio"
                                           ]].round(decimals=2)

weather_province.columns = ["avg_temp_mean",
                            "avg_rel_humidity_mean",
                            "max_wind_speed_mean",
                            "precipitation_mean",
                            "most_wind_direction",
                            "min_temp_mean",
                            "max_temp_mean",
                            "confirmed",
                            "released",
                            "deceased",
                            "elementary_school_count",
                            "kindergarten_count",
                            "university_count",
                            "nursing_home_count",
                            "academy_ratio",
                            "elderly_population_ratio",
                            "elderly_alone_ratio"]

# Getting geographical data on South Korea, cleaning and transforming it, setting index to a varaible with province names

south_korea = gpd.read_file('/Users/user/PycharmProjects/Capstone/Covid/gadm41_KOR_1.json')

south_korea.loc[:,"NAME_1" ]= south_korea.loc[:,"NAME_1"].replace('Jeju','Jeju-do')
"""
south_korea = south_korea[["NAME_1","geometry"]]
merge = pd.read_csv("/Users/user/PycharmProjects/Capstone/Covid/south_korea_data.csv", encoding="UTF-8")
merge = merge.set_index("NAME_1")
sejong = merge[merge.index == 'Sejong']
south_korea = pd.concat([south_korea, sejong])
south_korea = south_korea.sort_index()
"""
south_korea = south_korea.set_index("NAME_1")
#merge_map = pd.concat([south_korea,weather_province],join="outer",axis=1)

# Creating a list of dataframes with time series data for each province

time_province = time_province.reset_index()

l_1 = ['Busan', 'Chungcheongbuk-do', 'Chungcheongnam-do', 'Daegu', 'Daejeon',
       'Gangwon-do', 'Gwangju', 'Gyeonggi-do', 'Gyeongsangbuk-do',
       'Gyeongsangnam-do', 'Incheon', 'Jeju-do', 'Jeollabuk-do',
       'Jeollanam-do', 'Sejong', 'Seoul', 'Ulsan']
colors = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Indigo',
          'Violet', 'Black', 'White', 'Gray', 'Brown', 'Crimson',
          'Magenta', 'Cyan', 'Lavender', 'Maroon', 'Navy']
d = {}

timestamp_list = list(time_province["date"][time_province["province"]=="Busan"].reset_index(drop=True))
date_list = []
for timestamp in timestamp_list:
    date_list.append(str(timestamp.date()))

for i in l_1:
    d[i] = pd.DataFrame(columns=
        ['date','confirmed','released','deceased'])

province_list = list(d.values())
for i in range(len(province_list)):
    province_list[i]['date']=date_list
    province_list[i]['confirmed'] = list(time_province["confirmed"][time_province["province"]==l_1[i]].reset_index(drop=True))
    province_list[i]['released'] = list(time_province["released"][time_province["province"]==l_1[i]].reset_index(drop=True))
    province_list[i]['deceased'] = list(time_province["deceased"][time_province["province"]==l_1[i]].reset_index(drop=True))

for i in range(len(province_list)):
    province_list[i]['date'] = pd.to_datetime(province_list[i]['date'])
   # province_list[i] = province_list[i].set_index("date")


for i in range(len(province_list)):
    #province_list[i]['geometry'] = south_korea.loc[l_1[i], "geometry"]
    province_list[i]['province'] = l_1[i]


# Marging dataframes of the list into one dataframe which will be used for creating maps with animations
province_list_merged = pd.concat(province_list, axis=0)

# Data with geographical coordinates parsed to json:
south_korea_json = south_korea.to_json()
parsed = json.loads(south_korea_json)

# A dictionary for ticker values:

d_1 = {"avg_temp_mean":{"avg_temp_mean":"Average temperature"},
       "avg_rel_humidity_mean":{"avg_rel_humidity_mean":"Average relative humidity"},
       "max_wind_speed_mean":{"max_wind_speed_mean":"Maximum wind speed"},
       "precipitation_mean":{"precipitation_mean":"Precipitation"},
       "most_wind_direction":{"most_wind_direction":"Most wind direction"},
       "min_temp_mean":{"min_temp_mean":"Average minimal temperature"},
       "max_temp_mean": {"max_temp_mean":"Average maximum temperature"},
        "confirmed":{"confirmed":"Confirmed cases"},
        "released": {"released":"Released cases"},
        "deceased": {"deceased":"Deceased cases"},
        "elementary_school_count": {"elementary_school_count":"Numbers of elementary schools"},
       "kindergarten_count":{"kindergarten_count":"Numbers of kindergartens"},
        "university_count":{"university_count":"Numbers of universities"},
        "nursing_home_count":{"nursing_home_count":"Numbers of nursing homes"},
        "academy_ratio":{"academy_ratio":"Academy ratio"},
        "elderly_population_ratio":{"elderly_population_ratio":"Elderly population ratio"},
        "elderly_alone_ratio":{"elderly_alone_ratio":"Elderly alone ratio"}
       }
"""
    "kindergarten_count":"Numbers of elementary schools",
    "university_count":"Numbers of elementary schools",
    "nursing_home_count":"Numbers of elementary schools",
    "academy_ratio":"Academy ratio",
    "elderly_population_ratio":"Elderly population ratio",
    "elderly_alone_ratio":"Elderly alone ratio"
"""

#Another dictionary for ticker values:
d_2 = {"avg_temp_mean":(10,17),
    "avg_rel_humidity_mean":(55,70),
    "max_wind_speed_mean":(4,8),
    "precipitation_mean":(1,2),
    "most_wind_direction":(130,230),
    "min_temp_mean":(7,12),
    "max_temp_mean":(17,20),
    "confirmed":(0,7000),
    "released":(0,7000),
    "deceased":(0,100),
    "elementary_school_count":(0,1000),
    "kindergarten_count":(0,1500),
    "university_count":(0,100),
    "nursing_home_count":(400,50000),
    "academy_ratio":(0.95,1.5),
    "elderly_population_ratio":(10,30),
    "elderly_alone_ratio":(5,15)
}

# Layout:

app.layout = html.Div([
    html.Div([
    html.H2('COVID-19 cases, social and weather conditions in South Korea'),
    dcc.Graph(id="graph")],   style={'width': '80%', 'display': 'inline-block'}),
    html.Div([
    html.H4("Select option:"),
    dcc.Dropdown(
        id="ticker",
        options=[
    "confirmed",
    "released",
    "deceased",
    "avg_temp_mean",
    "avg_rel_humidity_mean",
    "max_wind_speed_mean",
    "precipitation_mean",
    "most_wind_direction",
    "min_temp_mean",
    "max_temp_mean"
    "elementary_school_count",
    "kindergarten_count",
    "university_count",
    "nursing_home_count",
    "academy_ratio",
    "elderly_population_ratio",
    "elderly_alone_ratio"],
        value="confirmed",
        clearable=False
    )],   style={'width': '20%', 'display': 'inline-block'})
])
#The function to running the app:

@app.callback(
    Output("graph", "figure"),
    Input("ticker", "value")
    )
def display_geo_map(ticker):
    fig = px.choropleth_mapbox(weather_province,
                        geojson=parsed,
                        locations=weather_province.index,
                        color=weather_province[ticker],
                        center={"lat": 36.441, "lon": 126.5316}, zoom=5.3,
                        range_color=d_2[ticker],
                        mapbox_style="carto-positron",
                        labels=d_1[ticker]
    )
    fig.update_layout(
        margin={"r": 1, "t": 1, "l": 1, "b": 1},
        #mapbox_accesstoken=token
    )
    return fig

#Running the app:
app.run_server(debug=True, port=8050)
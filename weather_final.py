
import requests
import os
from datetime import datetime


from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point


user_api = os.environ['current_weather_data']
location = input("Enter the city name: ")
count=0

complete_api_link = "https://api.openweathermap.org/data/2.5/weather?q="+location+"&appid="+user_api
api_link = requests.get(complete_api_link)
api_data = api_link.json()

#create variables to store and display data
temp_city = ((api_data['main']['temp']) - 273.15)
weather_desc = api_data['weather'][0]['description']
hmdt = api_data['main']['humidity']
wind_spd = api_data['wind']['speed']
date_time = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

print ("-------------------------------------------------------------")
print ("Weather Stats for - {}  || {}".format(location.upper(), date_time))
print ("-------------------------------------------------------------")

print ("Current temperature is: {:.2f} deg C".format(temp_city))
print ("Current weather desc  :",weather_desc)
print ("Current Humidity      :",hmdt, '%')
print ("Current wind speed    :",wind_spd ,'kmph')

poss=['light intensity shower rain', 'few clouds', 'snow', 'freezing rain', 'scattered clouds', 'thunderstorm with rain', 'thunderstorm with light rain', 'light intensity drizzle', 'sand', 'smoke', 'sky is clear', 'broken clouds', 'heavy intensity rain', 'drizzle', 'heavy snow', 'Sky is Clear', 'overcast clouds', 'thunderstorm', 'light thunderstorm', 'light rain', 'dust', 'light shower sleet', 'fog', 'proximity shower rain', 'mist', 'moderate rain', 'light shower snow', 'light snow', 'proximity moderate rain', 'rain and drizzle', 'haze']

disaster_name = input ("This input will have the name of the disaster: ")
poss_f=['light intensity shower rain','snow', 'freezing rain', 'freezing rain', 'scattered clouds', 'thunderstorm with rain', 'thunderstorm with light rain', 'light intensity drizzle', 'broken clouds', 'heavy intensity rain', 'drizzle', 'overcast clouds', 'thunderstorm', 'light thunderstorm', 'light rain', 'light shower sleet', 'proximity shower rain', 'moderate rain', 'light shower snow', 'light snow', 'proximity moderate rain', 'rain and drizzle']
poss_d=['light intensity shower rain','snow', 'freezing rain', 'freezing rain', 'thunderstorm with rain', 'thunderstorm with light rain', 'light intensity drizzle', 'heavy intensity rain', 'drizzle', 'thunderstorm', 'light thunderstorm', 'light rain', 'light shower sleet', 'proximity shower rain', 'moderate rain', 'light shower snow', 'light snow', 'proximity moderate rain', 'rain and drizzle']

proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')


def geodesic_point_buffer(lat, lon, km):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)
    return transform(project, buf).exterior.coords[:]

b = geodesic_point_buffer(45.4, -75.7, 100.0)
print ()

for i in b:
    count+=1
    if (count%7==0):
        complete_api_p2 = "https://api.openweathermap.org/data/2.5/weather?lat="+str(i[0]+13)+"&lon="+str(i[1]+13)+"&appid="+user_api
        api_link2 = requests.get(complete_api_p2)
        api_data2 = api_link2.json()    
        hmdt = api_data2['main']['humidity']
        print ("Weather Stats for - {}  || {}".format(location.upper(), date_time))
        print ("Long:",i[0],"Lat:",i[1])
        print ("Hum: ",hmdt,"%\n")
        

def dis_val(ext):
    
    if (ext=="flood"):
        if (weather_desc in poss_f):
            return 1
    
    if (ext=="earthquake"):
        return 1
    
    if (ext=="tordano"):
        if (wind_spd>64.35):
            return 1
        else:
            return 0
    
    if (ext=="cyclone"):
        if ((wind_spd>120) and (weather_desc in poss_f)):
            return 1
        else:
            return 0
    
    if (ext=="forest_fire"):
        if (weather_desc not in poss_d):
            return 1
        
    if (ext=="landslides"):
        return 1

out2 = dis_val(disaster_name)

if (out2 == 1):
    print ("Yes, there is a chance the news is true.")
    
else:
    print ("No, detected as fake news, weather contradictory.")

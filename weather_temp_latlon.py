
import requests
import os
from datetime import datetime

from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point

from configparser import ConfigParser

file = 'config2.ini'
config = ConfigParser()
config.read(file)

user_api = os.environ['current_weather_data']
location = ''
lat_con = config['info']['lat']
lon_con = config['info']['lon']

complete_api_link =  "https://api.openweathermap.org/data/2.5/weather?lat="+lat_con+"&lon="+lon_con+"&appid="+user_api
api_link = requests.get(complete_api_link)
api_data = api_link.json()

#create variables to store and display data
temp_city = ((api_data['main']['temp']) - 273.15)
weather_desc = api_data['weather'][0]['description']
hmdt = api_data['main']['humidity']
wind_spd = api_data['wind']['speed']
longit = api_data['coord']['lat']
latitu = api_data['coord']['lon']
date_time = datetime.now().strftime("%d %b %Y | %I:%M:%S %p")

print ("\n-------------------------------------------------------------")
print ("Weather Stats for - {} || {}".format(lat_con,lon_con))
print ("-------------------------------------------------------------")

print ("Current temperature is: {:.2f} deg C".format(temp_city))
print ("Current weather desc  :",weather_desc)
print ("Current Humidity      :",hmdt, '%')
print ("Current wind speed    :",wind_spd ,'kmph')

poss=['light intensity shower rain', 'few clouds', 'snow', 'freezing rain', 'scattered clouds', 'thunderstorm with rain', 'thunderstorm with light rain', 'light intensity drizzle', 'sand', 'smoke', 'sky is clear', 'broken clouds', 'heavy intensity rain', 'drizzle', 'heavy snow', 'Sky is Clear', 'overcast clouds', 'thunderstorm', 'light thunderstorm', 'light rain', 'dust', 'light shower sleet', 'fog', 'proximity shower rain', 'mist', 'moderate rain', 'light shower snow', 'light snow', 'proximity moderate rain', 'rain and drizzle', 'haze']

disaster_name = config['info']['disaster']
poss_f = ['light intensity shower rain','snow', 'freezing rain', 'freezing rain', 'scattered clouds', 'thunderstorm with rain', 'thunderstorm with light rain', 'light intensity drizzle', 'broken clouds', 'heavy intensity rain', 'drizzle', 'overcast clouds', 'thunderstorm', 'light thunderstorm', 'light rain', 'light shower sleet', 'proximity shower rain', 'moderate rain', 'light shower snow', 'light snow', 'proximity moderate rain', 'rain and drizzle']
poss_d = ['light intensity shower rain','snow', 'freezing rain', 'freezing rain', 'thunderstorm with rain', 'thunderstorm with light rain', 'light intensity drizzle', 'heavy intensity rain', 'drizzle', 'thunderstorm', 'light thunderstorm', 'light rain', 'light shower sleet', 'proximity shower rain', 'moderate rain', 'light shower snow', 'light snow', 'proximity moderate rain', 'rain and drizzle']

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

b = geodesic_point_buffer(longit, latitu, 100.0)
print ()

count=0
ac_count=0
humd_arr = [hmdt]
weat_dsc = [weather_desc]
wind_spe = [wind_spd]
temps_ct = [temp_city]

print ("========================================================\n")
for i in b:
    count+=1
    if (count%9==0):
        ac_count +=1
        complete_api_p2 = "https://api.openweathermap.org/data/2.5/weather?lat="+str(i[0])+"&lon="+str(i[1])+"&appid="+user_api
        api_link2 = requests.get(complete_api_p2)
        api_data2 = api_link2.json()
        temp_ct2 = ((api_data2['main']['temp']) - 273.15)   #alt val - 248.83
        hmdt2 = api_data2['main']['humidity']
        weather_desc2 = api_data2['weather'][0]['description']
        wind_spd2 = api_data2['wind']['speed']        
        print ("Weather Stats ",ac_count) #- {}  || {}".format(location.upper(), date_time)
        print ("Long: %.4f" % i[0],"Lat: %.4f" % i[1])
        print ("Humi:",hmdt2,"%")
        print ("Desc:",weather_desc2)
        print ("Wind:",wind_spd2,"kmph")
        print ("Temp: %.2f deg C\n" % temp_ct2)
        humd_arr.append(hmdt2)
        weat_dsc.append(weather_desc2)
        wind_spe.append(wind_spd2)
        temps_ct.append(temp_ct2)
        
def dis_val(ext,wind_spe,temps_ct,humd_arr,weat_dsc):
    if (ext=="flood"):
        for j in weat_dsc:
            if (j in poss_f):
                return 1
    
    if (ext=="earthquake"):
        return 1
        #BLANK RETURN
    
    if (ext=="tornado"):
        if (sum(wind_spe)/len(wind_spe) > 64.35):
            return 1
        else:
            return 0
    
    if (ext=="cyclone"):
        if (sum(wind_spe)/len(wind_spe) > 120):
            for j in weat_dsc:
                if (j in poss_f):
                    return 1
        else:
            return 0
    
    if (ext=="forest_fire"):
        for j in weat_dsc:
            if (j not in poss_d):
                return 1
                break
        return 0
        
    if (ext=="landslide"):
        return 1
        #BLANK RETURN
        
    if (ext=="heatwaves"):
        if (sum(temps_ct)/len(temps_ct) > 45):
            return 1
        else:
            return 0
    else:
        print ('Unspecified disaster, returning true.')
        return 1
        
out2 = dis_val(disaster_name,wind_spe,temps_ct,humd_arr,weat_dsc)

print (disaster_name)
if (out2 == 1):
    print ("Yes, there is a chance the news is true.")
    config.set('output','chances','1')
    
else:
    print ("No, detected as fake news, weather contradictory.")
    config.set('output','chances','0')

with open(file, 'w') as configfile:
    config.write(configfile)
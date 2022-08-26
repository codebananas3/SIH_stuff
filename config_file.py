
from configparser import ConfigParser

file = 'config2.ini'
config = ConfigParser()
config.read(file)

print (config.sections())
print (config['info']['city'])
print (config['info']['disaster'])

config.set('info','lat','72.8311')
config.set('info','lon','21.1702')
print (config['info']['lat'])
print (config['info']['lon'])

config.set('info','city','bihar')
print (config['info']['city'])

config.set('info','disaster','tornado')
print (config['info']['disaster'])

with open(file, 'w') as configfile:
    config.write(configfile)
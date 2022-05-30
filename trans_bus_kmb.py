import requests
import json
from os import path
import copy
import os
import time

def emitRequest(url):
  # retry if "Too many request (429)"
  while True:
    r = requests.get(url)
    if r.status_code == 200:
      return r
    elif r.status_code == 429:
      time.sleep(1)
    else:
      raise Exception(r.status_code, url)


def getRouteStop(co = 'kmb'):
    # define output name
    ROUTE_LIST = 'routeList.'+co+'.json'
    STOP_LIST = 'stopList.'+co+'.json'

    if path.isfile(ROUTE_LIST):
      os.remove(ROUTE_LIST)
    if path.isfile(STOP_LIST):
      os.remove(STOP_LIST)
    
    # load route list and stop list if exist
    routeList = {}
    #if path.isfile(ROUTE_LIST):
    if False:
        return
    else:
        # load routes
        r = emitRequest('https://data.etabus.gov.hk/v1/transport/'+co+'/route/')
        #r = requests.get('https://data.etabus.gov.hk/v1/transport/'+co+'/route/')
        for route in r.json()['data']:
            route['co'] = 'kmb'
            route['stops'] = {}
            routeList['+'.join([route['route'], route['service_type'], route['bound']])] = route

        # load route stops
        r = requests.get('https://data.etabus.gov.hk/v1/transport/'+co+'/route-stop/')
        for stop in r.json()['data']:
            routeKey = '+'.join([stop['route'], stop['service_type'], stop['bound']])
            if routeKey in routeList:
                routeList[routeKey]['stops'][int(stop['seq'])] = stop['stop']
            else:
                # if route not found, clone it from service type = 1
                _routeKey = '+'.join([stop['route'], str('1'), stop['bound']])
                routeList[routeKey] = copy.deepcopy(routeList[_routeKey])
                routeList[routeKey]['stops'] = {}
                routeList[routeKey]['stops'][int(stop['seq'])] = stop['stop']

        # flatten the route stops back to array
        for routeKey in routeList.keys():
            stops = [routeList[routeKey]['stops'][seq] for seq in sorted(routeList[routeKey]['stops'].keys())]
            routeList[routeKey]['stops'] = stops

        # flatten the routeList back to array
        routeList = [routeList[routeKey] for routeKey in routeList.keys() if not routeKey.startswith('K')]


    stopList = {}
    #if path.isfile(STOP_LIST):
    #    with open(STOP_LIST) as f:
    #        stopList = json.load(f)
    if False:
      return
    else:
        # load stops
        r = requests.get('https://data.etabus.gov.hk/v1/transport/'+co+'/stop')
        _stopList = r.json()['data']
        for stop in _stopList:
            stopList[stop['stop']] = stop
   
  
    #loop stoplist to get contained routes
    for key, stopMod in stopList.items():
        tmpContainRoute = []
        for routeMod in routeList:
            if stopMod['stop'] in routeMod['stops']:
                tmpSeq = routeMod['stops'].index(stopMod['stop'])
                tmpRoute = {}
                tmpRoute['ID'] = ('%s%s%s%s'%(routeMod['co'], routeMod['route'], routeMod['bound'], routeMod.get('service_type', '1')))
                tmpRoute['i'] = tmpSeq
                tmpContainRoute.append(tmpRoute)
        stopMod['routes'] = tmpContainRoute
  
  
    with open(ROUTE_LIST, 'w') as f:
        f.write(json.dumps(routeList, ensure_ascii=False))
    with open(STOP_LIST, 'w') as f:
        f.write(json.dumps(stopList, ensure_ascii=False))

getRouteStop()


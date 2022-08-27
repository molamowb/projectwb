
import requests
import json
from os import path
import asyncio
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


def getRouteStop(co):
    # define output name
    ROUTE_LIST = 'routeList.'+co+'.json'
    STOP_LIST = 'stopList.'+co+'.json'

    if path.isfile(ROUTE_LIST):
      os.remove(ROUTE_LIST)

    # load route list and stop list if exist
    routeList = {}
    
    if False:
        return
    else:
        # load routes
        #r = requests.get('https://rt.data.gov.hk/v1/transport/nlb/route.php?action=list')
        r = emitRequest('https://rt.data.gov.hk/v2/transport/nlb/route.php?action=list')
        routeList = []
        for route in r.json()['routes']:
            routeList.append({
                "co": co,
                "route_id": route['routeId'],
                "route": route['routeNo'],
                "bound": "O",
                "service_type": str(1 + route['overnightRoute'] * 2 + route['specialRoute'] * 4),
                "orig_tc": route['routeName_c'].split(' > ')[0],
                "orig_sc": route['routeName_s'].split(' > ')[0],
                "orig_en": route['routeName_e'].split(' > ')[0],
                "dest_tc": route['routeName_c'].split(' > ')[1],
                "dest_sc": route['routeName_s'].split(' > ')[1],
                "dest_en": route['routeName_e'].split(' > ')[1],
                "stops": []
            })

    _stops = []
    stopList = {}
    if path.isfile(STOP_LIST):
        with open(STOP_LIST) as f:
            stopList = json.load(f)
   
    def getRouteStop(routeId):
        r = requests.post('https://rt.data.gov.hk/v2/transport/nlb/stop.php?action=list', data = '{"routeId": "'+routeId+'"}')
        return r.json()['stops']

    async def getRouteStopList ():
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(None, getRouteStop, route['route_id']) for route in routeList]
        ret = []
        for future in futures:
            ret.append(await future)
        for route, stops in zip(routeList, ret):
            stopIds = []
            fares = []
            faresHoliday = []
            for stop in stops:
                if stop['stopId'] not in stopList:
                    stopList[stop['stopId']] = {
                        'stop': stop['stopId'],
                        'name_en': stop['stopName_e'],
                        'name_tc': stop['stopName_c'],
                        'name_sc': stop['stopName_s'],
                        'lat': stop['latitude'],
                        'long': stop['longitude']
                    }
                stopIds.append(stop['stopId'])
                fares.append(stop['fare'])
                faresHoliday.append(stop['fareHoliday'])
            route['stops'] = stopIds
            route['fares'] = fares[0:-1]
            route['faresHoliday'] = faresHoliday[0:-1]
        return routeList


    loop = asyncio.get_event_loop()
    routeList = loop.run_until_complete(getRouteStopList())

    #loop stoplist to get contained routes
    for key, stopMod in stopList.items():
        tmpContainRoute = []
        for routeMod in routeList:
            if stopMod['stop'] in routeMod['stops']:
                tmpSeq = routeMod['stops'].index(stopMod['stop'])
                tmpRoute = {}
                tmpRoute['ID'] = ('%s%s%s%s%s'%(routeMod['co'], routeMod['route_id'],  routeMod['route'], routeMod['bound'], routeMod.get('service_type', '1')))
                tmpRoute['i'] = tmpSeq
                tmpContainRoute.append(tmpRoute)
        stopMod['routes'] = tmpContainRoute
    
    
    with open(ROUTE_LIST, 'w') as f:
        f.write(json.dumps(routeList, ensure_ascii=False))
    with open(STOP_LIST, 'w') as f:
        f.write(json.dumps(stopList, ensure_ascii=False))

getRouteStop('nlb')

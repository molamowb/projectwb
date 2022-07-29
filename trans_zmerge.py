import json
from haversine import haversine, Unit

routeList = {}
stopList = {}
stopMap = {}

#def getRouteObj ( route, co, stops, bound, orig, dest, seq, fares, faresHoliday, freq, jt, nlbId, gtfsId, serviceType = '1'):
def getRouteObj ( co, route, bound, serviceType, stops, orig, dest, route_id):
  return {
    'co': co,
    'route_id': route_id,
    'route': route,
    'bound': bound,
    'service_type': serviceType,
    'stops': stops,
    'orig': orig,
    'dest': dest,
    #'fares': fares,
    #'faresHoliday': faresHoliday,
    #'freq': freq,
    #'jt': jt,
    #'nlbId': nlbId,
    #'gtfsId': gtfsId,
    #'seq': seq
  }


def importRouteListJson( co ):
  _routeList = json.load(open('routeList.%s.json'%co))
  _stopList = json.load(open('stopList.%s.json'%co))
  for stopId, stop in _stopList.items():
    if stopId not in stopList:
      stopList[stopId] = {
        'stop': stopId,
        'name': {
          #'en': stop['name_en'],
          #'tc': stop['name_tc'],
          #'sc': stop['name_sc']
          'en': stop.get('name_en', "en NA"),
          'tc': stop.get('name_tc', "tc NA"),
          'sc': stop.get('name_sc', "sc NA")
        },
        #'lat': stop['lat'],
        #'long': stop['long']
        'lat': str(stop.get('lat', "lat NA")),
        'long': str(stop.get('long', "long NA")),
        'routes': stop.get('routes', [])
      }
  for _route in _routeList:
    routeID = ('%s%s%s%s%s'%(_route['co'], _route.get('route_id', ''), _route['route'], _route['bound'], _route.get('service_type', '1')))
    orig = {'en': _route['orig_en'].replace('/', '／'),
            'tc': _route['orig_tc'].replace('/', '／'),
            'sc': _route['orig_sc'].replace('/', '／')
            }
            
    dest = {'en': _route['dest_en'].replace('/', '／'),
            'tc': _route['dest_tc'].replace('/', '／'),
            'sc': _route['dest_sc'].replace('/', '／')
            }
    routeList[routeID] = getRouteObj(
            co = _route['co'],
            #route_id = _route['route_id'] if _route['co'] == 'gmb' else "",
            route_id = _route.get('route_id', ''),
            route = _route['route'],
            bound = _route['bound'],
            serviceType = _route.get('service_type', '1'),
            stops = _route['stops'],
            orig = orig,
            dest = dest
          #fares = _route.get('fares', None),
          #faresHoliday = _route.get('faresHoliday', None),
          #freq = _route.get('freq', None),
          #jt = _route.get('jt', None),
          #nlbId = _route.get('id', None),
          #gtfsId = _route.get('gtfsId', None),
          #seq = len(_route['stops'])
    )
    
  
  
importRouteListJson('kmb')
importRouteListJson('ctb') 
importRouteListJson('nwfb')
importRouteListJson('gmb')
importRouteListJson('nlb')
importRouteListJson('lr')
importRouteListJson('mtrbus')
importRouteListJson('mtr')

#add gtfs
gtfs = json.load(open('gtfs.json'))


db = {
  'routeList': routeList,
  'stopList': stopList,
  'gtfsRouteList': gtfs['gtfsRouteList']
  #'holidays': holidays
}

with open( 'db.json', 'w' ) as f:
  f.write(json.dumps(db, ensure_ascii=False, separators=(',', ':')))

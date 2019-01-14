# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 15:31:45 2018

@author: selen
"""

import sys
import vessel_track as vs
from datetime import datetime

#path = os.path.abspath(os.path.join(os.path.dirname(__file__), "vesseldata.csv"))
path = 'C:\\Users\\selen\\Desktop\\vesseldata.csv' 
Main = vs.main()
vessels_df = Main.createVessels(path).sort_values(['vessel','timestamp'])
ports = Main.createPorts(vessels_df)
vessels_df = vessels_df.merge(ports)[['vessel','timestamp','port_id']].sort_values(['vessel','timestamp'])

#------------------->  Print trips for vessel 5291 in period 2017-10-13 10:00 - 2017-10-13 11:30
print("---------------------------------------------------------------------------------")
print("----------------- TEST 1 Print trips for vessel 5291 ----------------------------\n----------------- in period 2017-10-13 10:00 - 2017-10-13 11:30 -----------------" )
print("---------------------------------------------------------------------------------")
Main.printTrips(Main.getTrips(vessels_df,5291,['2017-10-13 10:00','2017-10-13 11:30']))

#------------------->  Print trips for vessel 4378 in period 2017-10-13 - 2017-10-13 12:00
print("---------------------------------------------------------------------------------")
print("----------------- TEST 2 Print trips for vessel 4378 ----------------------------\n----------------- in period 2017-10-13 - 2017-10-13 12:00 -----------------" )
print("---------------------------------------------------------------------------------")
Main.printTrips(Main.getTrips(vessels_df,4378,['2017-10-13','2017-10-13 12:00']))

#------------------->  Print all trips for vessel 5291 in all periods 
#-------------------> ATTENTION this line prints 3658 trips!
#Main.printTrips(Main.getTrips(vessels,4378,None))

#------------------->  Print all trips for all vessels in all periods
#-------------------> ATTENTION these lines print 8559 trips!
#for i in Main.getVessels(vessels):
#    k=0    
#    timeline = vessels[vessels['vessel']==i].timestamp.unique()
#    for j in range(len(timeline)-3000):
#        start = timeline[j]
#        end = timeline[j+1]
#        port_from = vessels[(vessels['vessel']==i) & (vessels['timestamp']==start)].port_id
#        port_to = vessels[(vessels['vessel']==i) & (vessels['timestamp']==end)].port_id
#        print('Vessel ', i, " trip no: ", k, " between ", start, "-", end , " from port ", port_from.unique()[0] , " to port ", port_to.unique()[0])
#        k += 1

#------------------->  Print all ports (in the order) that the vessel 4378...
#--------------------- ...has passed since the beginning

print("---------------------------------------------------------------------------------")
print("------- TEST 3 Print all trips for vessel 4378 since the beginning --------------" )
print("---------------------------------------------------------------------------------")
vessel_id=4378
limit = 183
print(Main.printAllTripOfVessel(Main.getAllTripOfVessel(vessels_df,vessel_id),vessel_id)[:limit] + "... for see all please delete limit here!" )
    

path_map = 'C:\\Users\\selen\\Desktop\\map.html' 
#------------------->  Print trip on map for vessel 4378 in period 2017-10-13 10:00 - 2017-10-13 15:30
list_ports = Main.getTrips(vessels_df,4378,['2017-10-13 10:00','2017-10-27 15:30'])
#-------------------> For all ports that the vessel 4378 has passed since the beginning 
#list_ports = Main.getTrips(vessels,4378,None)
list_lat, list_long = Main.getLatLong(Main.getPortListForTrip(list_ports),ports)
#Main.plotMap(list_lat,list_long,path_map)
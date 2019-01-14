# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 15:11:34 2018
@author: selen
"""
import pandas as pd
from datetime import datetime
import gmplot 
import os

class main(object):
    def __init__(self):
        pass
    def createVessels(self,path):
        return pd.read_csv(path, index_col=False)
    def createPorts(self,df_vessel):
        df_ports = df_vessel[df_vessel.columns[2:4]].drop_duplicates().sort_values(['latitude','longitude'])
        df_ports['port_id'] = range(1, len(df_ports) + 1)  
        return df_ports
    def getVessels(self,df_vessel):
        return df_vessel.vessel.unique()
    def getTrips(self,df_vessel,vessel_id,period):
        return_list = []
        if(not vessel_id in df_vessel.vessel.unique()):
            print("This vessel does not exists")
        else:
            vessels= df_vessel[(df_vessel['vessel']==vessel_id)]
            if(not period):
                print("Period not specified, if you want to print all trips please remove comments (Warning: that will be long!)")
                k=0    
                timeline = vessels.timestamp.unique()
                for j in range(len(timeline)-1):
                    start = timeline[j]
                    end = timeline[j+1]
                    port_from = vessels[vessels['timestamp']==start].port_id
                    port_to = vessels[vessels['timestamp']==end].port_id
                    return_list.append([vessel_id,k,start,end,port_from.unique()[0],port_to.unique()[0]])
                    #print('Vessel ', vessel_id, " trip no: ", k, " between ", start, "-", end , " from port ", port_from.unique()[0] , " to port ", port_to.unique()[0])
                    k += 1
            else:
                k=0
                timeline = vessels.timestamp.unique()
                for j in range(len(timeline)-1):
                    start = timeline[j]
                    end = timeline[j+1]
                    periods = []
                    for p in period:
                        time_format = "%Y-%m-%d %H:%M:%S.%f" if '.' in p else "%Y-%m-%d %H:%M" if ':' in p else "%Y-%m-%d"
                        periods.append(datetime.strptime(p, time_format))
                        
                    if(datetime.strptime(start,'%Y-%m-%d %H:%M:%S.%f') >=  periods[0] and datetime.strptime(end,'%Y-%m-%d %H:%M:%S.%f')  <= periods[1]):
                        port_from = vessels[vessels['timestamp']==start].port_id
                        port_to = vessels[vessels['timestamp']==end].port_id
                        return_list.append([vessel_id,k,start,end,port_from.unique()[0],port_to.unique()[0]])
                        #print('Vessel ', vessel_id, " trip no: ", k, " between ", start, "-", end , " from port ", port_from.unique()[0] , " to port ", port_to.unique()[0])
                        k += 1
        return return_list
    
    def printTrips(self,return_list):
        for i in return_list:
            print('Vessel ', i[0], " trip no: ", i[1], " between ", i[2], "-", i[3] , " from port ", i[4] , " to port ", i[5])

    def getAllTripOfVessel(self,df_vessels,vessel_id):
        return df_vessels[df_vessels['vessel']==vessel_id].port_id.unique()

    def printAllTripOfVessel(self,ports_list,vessel_id):
        i=0
        print_string=""
        print_string += "Vessel " + str(vessel_id) + " starts to trip -> "
        while i < len(ports_list):
            print_string += str(ports_list[i]) + "-> "
            i +=1
        print_string += "End of trip"
        return print_string
    
    def getPortListForTrip(self,return_list):
        l = []
        for i in range(len(return_list)):
            l.append(return_list[i][4])
            if(i==len(return_list)-1):
                l.append(return_list[i][5])
        return l
    
    def getLatLong(self,ports_list,df_ports):
        latitudes = []
        longitudes = []
        for i in ports_list:
            latitudes.append(df_ports[df_ports['port_id']==i].latitude.unique()[0])
            longitudes.append(df_ports[df_ports['port_id']==i].longitude.unique()[0])
        return latitudes, longitudes
    
    def plotMap(self,latitudes,longitudes,path_map):
        gmap3 = gmplot.GoogleMapPlotter(latitudes[0], longitudes[0], 4) 
        gmap3.scatter( latitudes, longitudes, '# FF0000', size = 40, marker = False ) 
        gmap3.plot(latitudes, longitudes,'cornflowerblue', edge_width = 2.5) 
        gmap3.apikey="#####################"
        gmap3.draw(path_map) 
        
        
    




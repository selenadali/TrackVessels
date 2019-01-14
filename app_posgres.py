# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 18:35:28 2018

@author: selen
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 20:13:00 2018

@author: selen

"""
#from: http://www.postgresqltutorial.com/postgresql-python/connect/


import sys, csv
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow,QTextEdit,QPushButton,QLabel,QLineEdit,QComboBox, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PyQt5.QtCore import pyqtSlot, Qt, QUrl
from PyQt5.QtWebKitWidgets import QWebView
import psycopg2
from configparser import ConfigParser
import pandas as pd
import vessel_track as vs


class App(object):
    def __init__(self):
        super().__init__()

    def config(self,section='postgresql'):
        filename = dbfile
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)
     
        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
     
        return db
                
    def create_tables(self):
        """ create tables in the PostgreSQL database"""
        commands = (
            """
            CREATE TABLE public.ports
            (
                port_id integer NOT NULL,
                latitude numeric NOT NULL,
                longitude numeric NOT NULL,
                CONSTRAINT ports_pkey PRIMARY KEY (port_id)
            )
            WITH (
                OIDS = FALSE
            )
            TABLESPACE pg_default;
            
            ALTER TABLE public.ports
                OWNER to postgres;
            """,
            """
            CREATE TABLE public.vessels
            (
                vessel integer NOT NULL,
                vessel_timestamp timestamp without time zone NOT NULL,
                vessel_port_id integer NOT NULL,
                CONSTRAINT vessel_port_id FOREIGN KEY (vessel_port_id)
                    REFERENCES public.ports (port_id) MATCH SIMPLE
                    ON UPDATE NO ACTION
                    ON DELETE NO ACTION
            )
            WITH (
                OIDS = FALSE
            )
            TABLESPACE pg_default;
            
            ALTER TABLE public.vessels
                OWNER to postgres;
            """)
        conn = None
        try:
            # read the connection parameters
            params = self.config()
            # connect to the PostgreSQL server
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            # create table one by one
            for command in commands:
                cur.execute(command)
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        
        
    def insert_data(self):
        conn = None
        port_id = None
        try:
            # read database configuration
            params = self.config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            # create a new cursor
            cur = conn.cursor()
            # execute the INSERT statement
            with open(path_ports, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip the header row.
                for row in reader:
                    cur.execute(
                        "INSERT INTO ports VALUES (%s, %s, %s)",
                        row
                    )
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
            
            cur = conn.cursor()
            # execute the INSERT statement
            with open(path_vessels, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip the header row.
                for row in reader:
                    cur.execute(
                        "INSERT INTO vessels VALUES (%s, %s, %s)",
                        row
                    )
            # commit the changes to the database
            conn.commit()
            # close communication with the database
            cur.close()
            
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
     
        return port_id
    
    def add_fuctions(self):
        commands = (""" 
                    CREATE OR REPLACE FUNCTION public.get_port_by_id(
                    	value_id integer)
                        RETURNS TABLE(port_id INT, latitude numeric, longitude numeric) 
                    AS $$
                    BEGIN
                     RETURN QUERY 
                     SELECT ports.port_id, ports.latitude, ports.longitude FROM public.ports
                    	--INNER JOIN public.vessels ON ports.port_id = vessels.vessel_port_id
                    	WHERE ports.port_id = value_id;
                    END;$$
                    LANGUAGE 'plpgsql';
                    """,
                    """CREATE OR REPLACE FUNCTION public.get_port_by_period(
                    	start_time timestamp without time zone,
                    	end_time timestamp without time zone)
                        RETURNS TABLE(vessel INT, vessel_timestamp timestamp without time zone, port_id INT, latitude numeric, longitude numeric) 
                    AS $$
                    BEGIN
                     RETURN QUERY 
                     SELECT vessels.vessel,vessels.vessel_timestamp,vessels.vessel_port_id,ports.latitude,ports.longitude FROM public.ports
                    	INNER JOIN public.vessels ON ports.port_id = vessels.vessel_port_id
                    	WHERE vessels.vessel_timestamp >= start_time and 
                    		  vessels.vessel_timestamp <= end_time;
                    END;$$
                    LANGUAGE 'plpgsql';
                     """,
                     """
                    CREATE OR REPLACE FUNCTION public.get_port_by_period_vessel_id(
                    	value_id integer,
                    	start_time timestamp without time zone,
                    	end_time timestamp without time zone)
                        RETURNS TABLE(vessel INT, vessel_timestamp timestamp without time zone, port_id INT, latitude numeric, longitude numeric) 
                    AS $$
                    BEGIN
                     RETURN QUERY 
                     SELECT vessels.vessel,vessels.vessel_timestamp,vessels.vessel_port_id,ports.latitude,ports.longitude FROM public.ports
                    	INNER JOIN public.vessels ON ports.port_id = vessels.vessel_port_id
                    	WHERE vessels.vessel_timestamp >= start_time and 
                    		  vessels.vessel_timestamp <= end_time and
                    		  vessels.vessel = value_id;
                    END;$$
                    LANGUAGE 'plpgsql';
                     """,
                     """
                    CREATE OR REPLACE FUNCTION public.get_trip_by_vessel_period(
                    	value_id integer,
                    	start_time timestamp without time zone,
                    	end_time timestamp without time zone)
                        RETURNS SETOF numeric[] 
                        LANGUAGE 'sql'
                    
                        COST 100
                        VOLATILE 
                        ROWS 1000
                    AS $BODY$ SELECT array[ports.latitude::numeric, ports.longitude::numeric] FROM public.ports
                    	INNER JOIN public.vessels ON ports.port_id = vessels.vessel_port_id
                    	WHERE vessels.vessel_timestamp >= start_time and 
                    		  vessels.vessel_timestamp <= end_time and
                    		  vessels.vessel = value_id
                    	ORDER BY vessels.vessel_timestamp$BODY$;
                    
                    ALTER FUNCTION public.get_trip_by_vessel_period(integer, timestamp without time zone, timestamp without time zone)
                        OWNER TO postgres;
                     """,
                     """
                    CREATE OR REPLACE FUNCTION public.get_vessel_by_id(
                    	value_id integer)
                        RETURNS TABLE(vessel integer, vessel_timestamp timestamp without time zone, port_id integer) 
                    AS $$
                    BEGIN
                     RETURN QUERY 
                     SELECT vessels.vessel,vessels.vessel_timestamp,vessels.vessel_port_id FROM public.ports
                    	INNER JOIN public.vessels ON ports.port_id = vessels.vessel_port_id
                    	WHERE vessels.vessel = value_id;
                    END;$$
                    LANGUAGE 'plpgsql';
                     """
             )
        conn = None
        try:
            # read the connection parameters
            params = self.config()
            # connect to the PostgreSQL server
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            # create table one by one
            for command in commands:
                cur.execute(command)
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
    
    def get_vessel(self,vessel_id):
        conn = None
        try:
            # read database configuration
            params = self.config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            # create a cursor object for execution
            cur = conn.cursor()
            # another way to call a stored procedure
            cur.callproc('get_vessel_by_id',(vessel_id,))
            # process the result set
            row = cur.fetchone()
            vessels = []
            while row is not None:
                vessels.append(row)
                row = cur.fetchone()
            return vessels
            # close the communication with the PostgreSQL database server
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
                
    def get_port_by_period(self,start_time,end_time):
        conn = None
        try:
            # read database configuration
            params = self.config()
            # connect to the PostgreSQL database
            conn = psycopg2.connect(**params)
            # create a cursor object for execution
            cur = conn.cursor()
            # another way to call a stored procedure
            cur.callproc('get_port_by_period',(start_time,end_time,))
            # process the result set
            row = cur.fetchone()
            vessels = []
            while row is not None:
                vessels.append(row)
                row = cur.fetchone()
            return vessels
            # close the communication with the PostgreSQL database server
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        
        
if __name__ == '__main__':
    app = App()
    dbfile = 'C:\\Users\\selen\\database.ini'
    
    #For create ports and vessels excel files (formatted)
    Main = vs.main()
    path = 'C:\\Users\\selen\\Desktop\\vesseldata.csv' 
    vessels = Main.createVessels(path).sort_values(['vessel','timestamp'])
    ports = Main.createPorts(vessels)
    vessels = vessels.merge(ports)[['vessel','timestamp','port_id']].sort_values(['vessel','timestamp'])
    ports.set_index('port_id', inplace=True)
    ports[['latitude','longitude']].to_csv("p.csv")
    vessels.set_index('vessel', inplace=True)
    vessels[['timestamp','port_id']].to_csv("v.csv")
    
    path_ports = 'C:\\Users\\selen\\p.csv' 
    path_vessels = 'C:\\Users\\selen\\v.csv' 
    
    #After create tables,inset data and add functions you can comment these 3 lines
    app.create_tables()
    app.insert_data()
    app.add_fuctions()
    
    #Tests get vessel, get trip by period...
    vessel_4378 = app.get_vessel(4378)    
    #print(vessel_4378, '\n\n')
    vessel_5291 = app.get_vessel(5291)    
    #print(vessel_5291)
    trip_1 = app.get_port_by_period('2017-10-13','2017-10-29 10:30')       
    #print(trip_1)
    





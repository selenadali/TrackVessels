# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 20:13:00 2018

@author: selen
"""
#I use the tutorial in http://zetcode.com/gui/pyqt5/

import sys, os
import vessel_track as vs
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow,QTextEdit,QPushButton,QLabel,QLineEdit,QComboBox, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PyQt5.QtCore import pyqtSlot, Qt, QUrl
from PyQt5.QtWebKitWidgets import QWebView

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Vessel - Trips'
        self.left = 20
        self.top = 30
        self.width = 1300
        self.height = 650
        self.initUI()
        

    def initUI(self):
        self.path = 'C:\\Users\\selen\\Desktop\\vesseldata.csv' 
        self.path_map = 'C:\\Users\\selen\\Desktop\\map.html'
        Main = vs.main()
        vessels = Main.createVessels(self.path).sort_values(['vessel','timestamp'])
        ports = Main.createPorts(vessels)
        vessels = vessels.merge(ports)[['vessel','timestamp','port_id']].sort_values(['vessel','timestamp'])

        self.lbl = QLabel("For see all the trips in a specific period please select a vessel number and start/end dates of period(You can try 2017-10-13 10:00 and 2017-10-27 15:30 for the vessel 4378)", self)
        self.cb = QComboBox(self)
        self.cb.addItem("Select Vessel")
        
        for i in vessels.vessel.unique():
            self.cb.addItem(str(i))
        self.cb.activated[str].connect(self.onActivated)     
        self.cb.currentIndexChanged.connect(self.selectionchange)
        
        self.qle = QLineEdit(self)
        self.qle.setText("Start date (ex: 2017-10-13)")
        self.first1 = True
        self.qle.textChanged[str].connect(self.onChanged1)

        self.qle2 = QLineEdit(self)
        self.qle2.setText("End date (ex: 2017-10-27 15:30)")
        self.first2 = True
        self.qle2.textChanged[str].connect(self.onChanged2)

        self.start = ""
        self.end = ""
        
        self.btn1 = QPushButton("Show Trips", self)
        self.btn1.clicked.connect(self.buttonClicked) 
        
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.cb)
        self.layout.addWidget(self.qle)
        self.layout.addWidget(self.qle2)
        self.layout.addWidget(self.btn1)
        self.layout.addWidget(self.lbl)
        self.setLayout(self.layout)
        self.show()

    def printPortList(self,return_list):
        self.editor = QTextEdit()
        self.editor.setTextInteractionFlags(Qt.NoTextInteraction)    
        self.editor.setText(vs.main.printAllTripOfVessel(self,return_list, self.vessel_id))

    def createTable(self,return_list):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(return_list))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setColumnWidth(0, 30)
        self.tableWidget.setColumnWidth(1, 160)
        self.tableWidget.setHorizontalHeaderLabels(( "Departure Time", "Arrival Time", "Departure Port" , "Arrival Port"))

        for i in range(len(return_list)):
            for j in range(4):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(return_list[i][j+2])))
        self.tableWidget.move(50, 50)
        self.tableWidget.resizeColumnsToContents()

    def onActivated(self, text):
        self.lbl.adjustSize()  
        self.vessel_id = int(text)
    
    def onChanged1(self, text):
        self.lbl.adjustSize() 
        if(self.first1):
            self.qle.setText("")
        self.first1 = False
        try:
            time_format = "%Y-%m-%d %H:%M:%S.%f" if '.' in text else "%Y-%m-%d %H:%M" if ':' in text else "%Y-%m-%d"
            self.start_date = datetime.strptime(text, time_format)
            self.start = text
        except ValueError:
            print("Please check the format of date 1 (YYYY-MM-DD or YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS.ss")

    def onChanged2(self, text):
        self.lbl.adjustSize() 
        if(self.first2):
            self.qle2.setText("")
        self.first2 = False
        try:
            time_format = "%Y-%m-%d %H:%M:%S.%f" if '.' in text else "%Y-%m-%d %H:%M" if ':' in text else "%Y-%m-%d"
            self.end_date = datetime.strptime(text, time_format)
            self.end = text
        except ValueError:
            print("Please check the format of date 2 (YYYY-MM-DD or YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS.ss")
          
    def buttonClicked(self):
        try:
            self.layout.removeWidget(self.tableWidget)
            self.layout.removeWidget(self.btn2)
            self.editor.move(1300,1000)
            self.layout.removeWidget(self.editor)
            self.layout.removeWidget(self.btn3)

        except:
            pass
        
        sender = self.sender()
        print(sender.text() + ' was pressed')
        Main = vs.main()
        vessels = Main.createVessels(self.path).sort_values(['vessel','timestamp'])
        ports = Main.createPorts(vessels)
        vessels = vessels.merge(ports)[['vessel','timestamp','port_id']].sort_values(['vessel','timestamp'])
        if(self.start == "" or self.end == ""):
            print("Please check the format of date 2 (YYYY-MM-DD or YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS.ss")
        period = [self.start, self.end]
        return_list = vs.main.getTrips(self, vessels, self.vessel_id, period)
        self.createTable(return_list)
        self.layout.addWidget(self.tableWidget)
        self.btn2 = QPushButton("Show All Trip of Vessel " + str(self.vessel_id), self)
        self.btn2.clicked.connect(self.buttonClicked2) 
        self.btn2.move(50,50)
        self.layout.addWidget(self.btn2)
        self.btn3 = QPushButton("Show This Trip On Map ", self)
        self.btn3.clicked.connect(self.buttonClicked3) 
        self.btn3.move(50,50)
        self.layout.addWidget(self.btn3)

    def buttonClicked2(self):
        try:
            self.layout.removeWidget(self.editor)
        except:
            pass
        sender = self.sender()
        print(sender.text() + ' was pressed')
        Main = vs.main()
        vessels = Main.createVessels(self.path).sort_values(['vessel','timestamp'])
        ports = Main.createPorts(vessels)
        vessels = vessels.merge(ports)[['vessel','timestamp','port_id']].sort_values(['vessel','timestamp'])
        return_list = vs.main.getAllTripOfVessel(self, vessels,self.vessel_id)
        self.printPortList(return_list)
        self.layout.addWidget(self.editor)

    def buttonClicked3(self):
        Main = vs.main()
        vessels = Main.createVessels(self.path).sort_values(['vessel','timestamp'])
        ports = Main.createPorts(vessels)
        vessels = vessels.merge(ports)[['vessel','timestamp','port_id']].sort_values(['vessel','timestamp'])
        period = [self.start, self.end]
        list_ports = Main.getTrips(vessels, self.vessel_id, period)
        list_lat, list_long = Main.getLatLong(Main.getPortListForTrip(list_ports),ports)
        Main.plotMap(list_lat,list_long,self.path_map)
        
        self.browser = QWebView()
        local_url = QUrl.fromLocalFile(self.path_map)
        print(local_url)
        self.browser.load(local_url)
        self.browser.show()
        self.browser.pop()
        
    def selectionchange(self,i):
      print("Items in the list are :")
      for count in range(self.cb.count()):
         print(self.cb.itemText(count))
      print("Current index",i,"selection changed ",self.cb.currentText())
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
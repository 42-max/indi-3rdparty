#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
# INDUINO METEOSTATION
# http://induino.wordpress.com 
# 
# NACHO MAS 2013

import sys, os
import rrdtool
import time
from meteoconfig import *
import math
from time import gmtime

from indiclient import *
import signal
import simplejson
import gc
#from guppy import hpy

signal.signal(signal.SIGINT, signal.SIG_DFL)

blue="0080F0"
orange="F08000"
red="FA2000"
white="AAAAAA"

P0=math.floor(1013.25/math.exp(ALTITUDE/8000.))
Pdelta=25
Pmin=P0-Pdelta
Pmax=P0+Pdelta

preamble=["--width","600",
         "--height","300",
         "--color", "FONT#FF0000",
	 "--color", "SHADEA#00000000",
	 "--color", "SHADEB#00000000",
	 "--color", "BACK#00000000",
	 "--color", "CANVAS#00000000"]

def graphs(time):
	ret = rrdtool.graph( CHARTPATH+"temp"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Temperature",
	 "--vertical-label=Celsius ºC",
	 "DEF:T="+RRDFILE+":T:AVERAGE",
	 "DEF:Tmax="+RRDFILE+":T:MAX",
	 "DEF:Tmin="+RRDFILE+":T:MIN",
	 "DEF:Dew="+RRDFILE+":Dew:AVERAGE",
	 "LINE1:T#"+red+":Ambient Temperature",
	 "HRULE:0#00FFFFAA:ZERO",
	 "AREA:Dew#"+red+"40:Dew Point\\r",
	 "COMMENT:\\n",
	 "GPRINT:T:AVERAGE:Avg Temp\: %6.2lf %S\\r")

	ret = rrdtool.graph( CHARTPATH+"alltemp"+str(time)+".png","-A","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Temperaturas",
	 "--vertical-label=Celsius ºC",
	 "DEF:IR="+RRDFILE+":IR:AVERAGE",
	 "DEF:Thr="+RRDFILE+":Thr:AVERAGE",
	 "DEF:Tp="+RRDFILE+":Tp:AVERAGE",
	 "DEF:Tir="+RRDFILE+":Tir:AVERAGE",
	 "DEF:Dew="+RRDFILE+":Dew:AVERAGE",
	 "LINE1:IR#00F0F0:IR",
	 "LINE1:Thr#00FF00:Thr",
	 "LINE1:Tp#FF0000:Tp",
	 "LINE1:Tir#0000FF:Tir",
	 "HRULE:0#00FFFFAA:ZERO",
	 "AREA:Dew#00008F10:Dew\\r")


	ret = rrdtool.graph( CHARTPATH+"pressure"+str(time)+".png","-A","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Pressure",
	 "--vertical-label=mBars",
	 "-u",str(Pmax),
	 "-l",str(Pmin),
	 "-r",
	 "DEF:P="+RRDFILE+":P:AVERAGE",
	 "HRULE:"+str(P0)+"#"+red+"AA:standard",
	 "LINE1:P#"+blue+":P\\r",
	 "COMMENT:\\n",
	 "GPRINT:P:AVERAGE:Avg P\: %6.2lf %S\\r")

	ret = rrdtool.graph( CHARTPATH+"hr"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "-u","105",
	 "-l","-5",
	 "-r",
	 "--title","Humidity",
	 "--vertical-label=%",
	 "DEF:HR="+RRDFILE+":HR:AVERAGE",
	 "HRULE:100#FF00FFAA:100%",
	 "HRULE:0#00FFFFAA:0%",
	 "LINE1:HR#"+blue+":HR\\r",
	 "COMMENT:\\n",
	 "GPRINT:HR:AVERAGE:Avg HR\: %6.2lf %S\\r")

	ret = rrdtool.graph( CHARTPATH+"light"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Iradiance",
	 "--vertical-label=rel",
	 "DEF:Light="+RRDFILE+":Light:AVERAGE",
	 "LINE1:Light#"+blue+":Irradiance\\r",
	 "COMMENT:\\n",
	 "GPRINT:Light:AVERAGE:Avg Light\: %6.2lf %S\\r")

	ret = rrdtool.graph( CHARTPATH+"clouds"+str(time)+".png","-A","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Clouds",
	 "--vertical-label=%",
	 "-u","102",
	 "-l","-2",
	 "-r",
	 "DEF:clouds="+RRDFILE+":clouds:AVERAGE",
	 "DEF:cloudFlag="+RRDFILE+":cloudFlag:AVERAGE",
	 "CDEF:cloudy=clouds,cloudFlag,*",
	 "LINE1:clouds#"+orange+":clouds",
	 "AREA:cloudy#FFFFFF40:CloudyFlag\\r",
	 "AREA:30#00000a40:Clear",
	 "AREA:40#0000AA40:Cloudy:STACK",
	 "AREA:32#0000FF40:Overcast:STACK")

	ret = rrdtool.graph( CHARTPATH+"skyT"+str(time)+".png","--start","-"+str(time)+"h","-E",
          preamble,
	 "--title","Sky Temperatures",
	 "--vertical-label=Celsius ºC",
	 "DEF:skyT="+RRDFILE+":skyT:AVERAGE",
	 "DEF:IR="+RRDFILE+":IR:AVERAGE",
	 "DEF:Thr="+RRDFILE+":Thr:AVERAGE",
	 "CDEF:Tc=IR,skyT,-",
	 "LINE1:skyT#"+blue+":Corrected Sky T",
	 "LINE1:IR#"+orange+":Actual Sky T",
	 "LINE1:Thr#"+red+":Ambient T",


def recv_indi_old():
	tim=time.localtime()
        HR=indi.get_float(INDIDEVICE,"HR","HR")
        Thr=indi.get_float(INDIDEVICE,"HR","T")
        P=indi.get_float(INDIDEVICE,"Presure","P")
        Tp=indi.get_float(INDIDEVICE,"Presure","T")
        IR=indi.get_float(INDIDEVICE,"IR","IR")
        Tir=indi.get_float(INDIDEVICE,"IR","T")
        dew=indi.get_float(INDIDEVICE,"Meteo","DEW")
        light=indi.get_float(INDIDEVICE,"SQM","SQM")
        T=indi.get_float(INDIDEVICE,"Meteo","T")
        clouds=indi.get_float(INDIDEVICE,"Meteo","clouds") 
        skyT=indi.get_float(INDIDEVICE,"Meteo","SkyT") 
        statusVector=indi.get_vector(INDIDEVICE,"STATUS")
	cloudFlag=int(statusVector.get_element("clouds").is_ok())
	dewFlag=int(statusVector.get_element("dew").is_ok())
	frezzingFlag=int(statusVector.get_element("frezzing").is_ok())
	return (("HR",HR),("Thr",Thr),("IR",IR),("Tir",Tir),("P",P),("Tp",Tp),("Dew",dew),("Light",light),
           ("T",T),("clouds",clouds),("skyT",skyT),("cloudFlag",cloudFlag),("dewFlag",dewFlag),
           ("frezzingFlag",frezzingFlag))

def recv_indi():
	tim=time.localtime()
        vectorHR=indi.get_vector(INDIDEVICE,"Humidity")
	HR=vectorHR.get_element("HR").get_float()
	Thr=vectorHR.get_element("T").get_float()

        vectorPressure=indi.get_vector(INDIDEVICE,"Pressure")
	P=vectorPressure.get_element("P").get_float()
	Tp=vectorPressure.get_element("T").get_float()

        vectorIR=indi.get_vector(INDIDEVICE,"IR")
	IR=vectorIR.get_element("IR").get_float()
	Tir=vectorIR.get_element("T").get_float()

        vectorMeteo=indi.get_vector(INDIDEVICE,"WEATHER_PARAMETERS")
	dew=vectorMeteo.get_element("WEATHER_DEWPOINT").get_float()
	clouds=vectorMeteo.get_element("WEATHER_CLOUD_COVER").get_float()
	T=vectorMeteo.get_element("WEATHER_TEMPERATURE").get_float()
        skyT=vectorMeteo.get_element("WEATHER_SKY_TEMPERATURE").get_float()

        vectorSQM=indi.get_vector(INDIDEVICE,"Sky Quality")
	sqm=vectorSQM.get_element("SQM").get_float()
   
        statusVector=indi.get_vector(INDIDEVICE,"WEATHER_STATUS")
	cloudFlag=int(statusVector.get_element("clouds").is_ok())
	dewFlag=int(statusVector.get_element("dew").is_ok())
	frezzingFlag=int(statusVector.get_element("frezzing").is_ok())
  
	return (("HR",HR),("Thr",Thr),("IR",IR),("Tir",Tir),("P",P),("Tp",Tp),("Dew",dew),("SQM",sqm),
           ("T",T),("clouds",clouds),("skyT",skyT),("cloudFlag",cloudFlag),("dewFlag",dewFlag),
           ("frezzingFlag",frezzingFlag))

#!/usr/bin/env python

import signal
import time
import sys
import os
import datetime
import mysql.connector

from pirc522 import RFID

run = True
sector = 11
lector=RFID()
util=lector.util()
bloque = util.block_addr(sector, 0)

def end_read(signal,frame):
    global run
    print("\nCtrl+C, cerrando programa")
    run = False
    lector.cleanup()
    sys.exit()

signal.signal(signal.SIGINT, end_read)
print("Arancando a leer")

while run:
	lector.wait_for_tag()
	(error, data) = lector.request()
	(error, uid) = lector.anticoll()
	if not error:
		util.set_tag(uid)
		#print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
        util.auth(lector.auth_a, [0x44,0x41,0x4A,0x47,0x4E,0x45])
        util.do_auth(bloque)
        #util.read_out(bloque)
        (fallo,tag)=lector.read(bloque)
        if not fallo:
		  print("Etiqueta leida")
        else:
		  print("Error de lectura")
		  continue


#######
        #print(tag)
        #print(type(tag[1]))
        tagHex=map(lambda x:hex(x),tag)
        #print(tagHex)
  #   for tag_now in tags:         
  #       yaEsta=False
 ###        tag_nowEPCString=tag_now.epc.decode('ascii')
        owns=tagHex[:8]
        ownsString=""
        for x in range(0,len(owns)):
		  ownsString=ownsString+str((owns[x][2:]))  
        if ownsString.upper()=="44414A474E455352":
		  cnx = mysql.connector.connect(user='root',password='raspberry',host='127.0.0.1',database='control')
		  cursor=cnx.cursor()
		  query = ("SELECT EPC FROM blacklist WHERE EPC='%s'")
		  tag_EPCString=""
		  for x in range(0,len(tagHex)):
		    tag_EPCString=tag_EPCString+str((tagHex[x][2:])) 
		  cursor.execute(query % tag_EPCString)
		  yaEsta=False
		  for (EPCEsta) in cursor:
			  yaEsta=True
			  print("Etiqueta en blacklist")
			  			  
		  if not yaEsta:
			  print(yaEsta)
			  add_EPC="INSERT INTO entradas(EPC,time) VALUES(%s,%s)"
			  add_EPCBlacklist="INSERT INTO blacklist (EPC,time) VALUES (%s, %s)"
			  ts = time.time()
			  timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
			  data=(tag_EPCString,timestamp)
			  cursor.execute(add_EPC,data)
			  cnx.commit()
			  cursor.execute(add_EPCBlacklist,data)
			  cnx.commit()
		  cnx.close()
	time.sleep(0.1)


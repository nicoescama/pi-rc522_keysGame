#!/usr/bin/env python

import signal
import time
import sys

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

print("Acerca una etiqueta nfc")
while run:
   lector.wait_for_tag()
   (error, data) = lector.request()
   #if not error:
	  #print("\nDetected: "+ format(data,"02x"))
   (error, uid) = lector.anticoll()
   if not error:
      #print("Card UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))     
      util.set_tag(uid)	  
      util.auth(lector.auth_a, [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF])
      #util.read_out(bloque)    
      util.write_trailer(sector,(0x44,0x41,0x4A,0x47,0x4E,0x45), (0xFF, 0x0F, 0x00), 105,(0x44,0x41,0x4A,0x47,0x4E,0x45))
      util.deauth()
      lector.wait_for_tag()
      (error, data) = lector.request()
      (error, uid) = lector.anticoll()
      if not error:		  
		  util.set_tag(uid)
		  util.auth(lector.auth_a, [0x44,0x41,0x4A,0x47,0x4E,0x45])
		  falla=util.do_auth(bloque)
		  #util.read_out(bloque)
		  #util.dump()
		  if not falla:
			  print("Confirmada la llave")
		  else:
			  print("algo ha fallado con la llave")
			  sys.exit()
		  util.read_out(bloque)
		  data = []
		  nombre=raw_input("ingresa 8 numeros hexa separados por coma\n")
		  nombreList=nombre.split(",")
		  data.append(0x44)
		  data.append(0x41)
		  data.append(0x4A)
		  data.append(0x47)
		  data.append(0x4E)
		  data.append(0x45)
		  data.append(0x53)
		  data.append(0x52)
		  if len(nombreList)==8:
			  try:
			     for i in range(0,len(nombreList)):
  				    data.append(int(nombreList[i],16))
			  except ValueError:
				 print "Error de formato"
				 continue
		  else:
				print "Escribe 8 numeros hexa separados por coma"
				continue
		  print(len(data))
		  util.auth(lector.auth_a, [0x44,0x41,0x4A,0x47,0x4E,0x45])
		  util.do_auth(bloque)
		  fallo=lector.write(bloque,data)
		  if not fallo:
			  print("etiqueta marcada correctamente")
			  sys.exit()
		  else:
			  print("Hubo un error al nombrar, vuelve a empezar")
		  
		 
		 
		  
		  
      

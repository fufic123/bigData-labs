#!/usr/bin/env python
import sys

sys.stdin = open("duom_cut.txt","r")
sys.stdout = open("mapout.txt","w")


for line in sys.stdin:
    line = line.strip()
    line = line[2:len(line)-2]
    susstring = line.split('}}{{')
    for stopas in susstring:
      #Sustojimo klientu skaicius
      klientai = None
      #sustojimo savaites diena
      diena = None
      parstrings = stopas.split('}{')
      for parstring in parstrings: 
        (vardas, reiksme) = parstring.split('=')
        if(reiksme != ''):
          if(vardas == 'Sustojimo klientu skaicius'):
            klientai=int(reiksme)
          if(vardas == 'sustojimo savaites diena'):
            diena=int(reiksme)
      if(klientai != None and diena != None):
        print('%s\t%s' % (diena, klientai))
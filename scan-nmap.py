#!/usr/bin/env python3
import socket
import os
import threading
import sys
from queue import Queue
from datetime import datetime
import argparse


target = ''

open_ports = []

q = Queue()

lock = threading.Lock()

def portscan(port):
   global open_ports
   soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

   try:
      con = soc.connect((target, port))
      with lock:
         print(f"Port {port}")
         open_ports.append(str(port))
      con.close()
   except (ConnectionRefusedError, AttributeError, OSError):
      pass

def threader():
   while True:
      port = q.get()
      portscan(port)
      q.task_done()

def main(args):
   global q, target
   socket.setdefaulttimeout(1)
   if (args.host == ""):
      target = input("Input IP address or URL : ")

   try:
      target = socket.gethostbyname(target)
   except (UnboundLocalError, socket.gaierror):
      print("[-] Error IP or web address")
      sys.exit()

   print("-" * 60)
   print(f"Scanning all port open target : {target}")
   print(f"Time started: {str(datetime.now())}")
   print("-" * 60)
   print("Open ports:")

   t1 = datetime.now()

   for port in range(1, 65536):
      q.put(port)

   for x in range(int(args.thread)):
      t = threading.Thread(target = threader)
      t.daemon = True
      t.start()

   q.join()

   t2 = datetime.now()
   total = t2 - t1
   print("Port scan completed in "+str(total))
   print("-" * 60)
   print("Running extensive nmap on open ports :")
   cmd_nmap = f"nmap -p{','.join(open_ports)} -sV -sC -T4 -Pn -oA result {target}"
   print(cmd_nmap)
   print("-" * 60)

   #Nmap
   try:
      if os.path.exists("nmap")==False:
         os.mkdir("nmap")
      os.chdir("nmap")
      os.system(cmd_nmap)
      t3 = datetime.now()
      total1 = t3 - t1
      print("-" * 60)
      print("Nmap completed in "+str(total1))
   except FileExistsError as e:
      print(e)
      sys.exit()

if __name__ == '__main__':
   try:
      parser = argparse.ArgumentParser(prog='Scanner')

      parser.add_argument('-t','--thread',default=300,help="Default : 300")
      parser.add_argument('-i','--host',default="",help="IP Address")
      args = parser.parse_args()
      main(args)
   except KeyboardInterrupt:
      print("Goodbye")
      sys.exit()
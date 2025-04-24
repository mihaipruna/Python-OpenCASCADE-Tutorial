from http.server import BaseHTTPRequestHandler
# -*- coding: utf-8 -*-
"""
@author: Mihai Pruna
use at own risk, no warranty implied or provided
"""
#server class to handle requests
import cgi
from CADprocessor import CADProcessorClass

class FServer(BaseHTTPRequestHandler):
  linecnt=0;
    
  def do_HEAD(self):
    return
    
  def do_GET(self):
    self.respond()
  #this function will respond to file upload via POST  
  def do_POST(self):
    ctype, pdict = cgi.parse_header(self.headers['content-type'])
    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
    postvars = cgi.parse_multipart(self.rfile, pdict)
    mycommand=postvars.get('datext')[0].decode('utf-8')  
    #save uploaded file locally
    myfilename=postvars.get('dafilename')[0].decode('utf-8')  
    self.writeBinaryData(postvars.get('dafile')[0],myfilename)
    self.send_response(200)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    #generate response depending on command         
    theresponse=self.ProcessFormData(mycommand,myfilename)
    self.wfile.write(bytes(theresponse, 'UTF-8'));
   
  def handle_http(self, status, content_type):
    self.send_response(status)
    self.send_header('Content-type', content_type)
    self.end_headers()
    return bytes('Hello World', 'UTF-8')
    
  def respond(self):
    content = self.handle_http(200, 'text/html')
    self.wfile.write(content)
    
  def showFileStats(self):
    return bytes(str(self.linecnt), 'UTF-8')


  def finish(self):
    if not self.wfile.closed:
        self.wfile.flush()
    self.wfile.close()
    self.rfile.close()
    
    
  def writeBinaryData(self,binaryData,filename):
    f = open(filename, "wb")
    f.write(binaryData)   
    
   #only Render which uses Python OCC to generate triangulation as string 
  def ProcessFormData(self,theCommand,theFilename):
      if theCommand=="Render":
          myCADProc=CADProcessorClass()
          newfile=myCADProc.SaveTriangulation(theFilename)
          commandresponse=""
          with open(newfile, 'r') as file:
              commandresponse = file.read().replace('\n', '')
          return commandresponse    
      
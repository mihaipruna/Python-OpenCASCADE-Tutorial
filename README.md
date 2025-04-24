# cadservertutorial
 tutorial on using Python and openCASCADE to process CAD models
 
 This tutorial will show you how to set up a CAD server for processing models submitted via a client web page. The client page will display the 3D model submitted. Note that only free software libraries are used. If you ever wanted to set up your own CAD system in the cloud, this is the tutorial for you!

A server written in Python is using pythonOCC to process CAD models and commands and return a mesh triangulation. The client web page displays the 3D model using THREE.js. 


We used the Spyder IDE for Python for coding and debugging this project. If you don’t have it, please install it using Anaconda.Likewise, if any Python packages mentioned in this tutorial are missing, please install them from the Anaconda command prompt.

Set up a project folder with three Python files: CADprocessor.py, main.py and myserver.py. We will cover each file separately. You can download the tutorial files below.

 

CADProcessor.py is the class that handles CAD file processing and triangulation. Only IGES files supported in this tutorial. You should be familiar with the basics of pythonOCC from our tutorial linked earlier in this article.

# -*- coding: utf-8 -*-
"""
@author: Mihai Pruna
use at own risk, no warranty implied or provided
"""


#load needed libraries
from OCC.IGESControl import IGESControl_Reader
from OCC.StlAPI import StlAPI_Writer
from OCC.BRepMesh import BRepMesh_IncrementalMesh
#this class holds functions for manipulating CAD files with PythonOCC
class CADProcessorClass():
    #saves STL file
    def SaveTriangulation(self,filename):
        #create new IGES reader class
        reader = IGESControl_Reader()
        #read file, make sure you update path. Note in Windows slash needs to be used
        reader.ReadFile(filename)
        #no idea what this does but without it the shape won't be created :)
        reader.TransferRoots()
        #generate Shape
        shape = reader.Shape()
        #mesh shape
        mesh = BRepMesh_IncrementalMesh(shape, 0.5, True, 0.5, True)
        #save STL file on server
        stl_writer = StlAPI_Writer()
        stl_writer.Write(shape,"tris.stl")
        return "tris.stl"



myserver.py is the class that handles POST requests from the client web page. Requests contain the file name, the file content, and a command string. Only command supported in this tutorial is Render, which generates STL triangulation of the CAD file (only IGES supported) and returns it to the client. 

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
      
 

main.py is the entry point. It starts the server locally. You can run this one from the Anaconda prompt in the same folder where the file is located with python main.py or from Spyder.

# -*- coding: utf-8 -*-
"""
@author: Mihai Pruna
use at own risk, no warranty implied or provided
"""
#!/usr/bin/env python3

#entry file, starts server
import time
from http.server import HTTPServer
from myserver import FServer
#run locally
HOST_NAME = 'localhost'
PORT_NUMBER = 8000

if __name__ == '__main__':
    httpd = HTTPServer((HOST_NAME, PORT_NUMBER), FServer)
    print(time.asctime(), 'Server UP - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server DOWN - %s:%s' % (HOST_NAME, PORT_NUMBER))
 

The file client.html is a web page with a mix of HTML and Javascript. Rather than the entire THREE.js, only the libraries needed are referenced (and included in the download package at the bottom of this page). When the server is running, you can upload an IGES file (one included in download package) and type Render in the text field. The file should be processed by the server and displayed on the page.

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<!--Author: Mihai Pruna. use at own risk, no warranty implied or provided-->
<html xmlns="http://progmodcon.com">
<head>
	<!--Load libraries-->
    <script type="text/javascript" src="sources/jquery-3.1.1.js"> </script>
	<script type="text/javascript" src="sources/jquery-3.1.1.min.js"> </script>
	<script type="text/javascript" src="sources/three.min.js"></script>
	<script type="text/javascript", src="sources/STLLoader.js"></script>
	<script src="sources/TrackballControls.js"></script>
</head>
<body>
	<!--Create form for upload of file and command-->
	<form id="myformid" enctype="multipart/form-data" method="post" action="http://localhost:8000/">
	  <input id="myfileid" name="file" type="file"/>
	  <p><label>Command field: <input name="command" type="text" id="command-id" /></label></p>
	  <input type="submit" id="submitid" value="Upload"/>
	  <script>
		//retrieve elements from document
	    var form = document.getElementById('myformid');
		var fileSelect = document.getElementById('myfileid');
		var uploadButton = document.getElementById('submitid');
		var commandstring=document.getElementById('command-id');
		//gets called when upload button pushed
		form.onsubmit = function(event) {
		  event.preventDefault();
		  // Update button text.
		  uploadButton.innerHTML = 'Uploading...';
          // Get the selected files from the input.
		  var files = fileSelect.files;
		  // Create a new FormData object.
		  var formData = new FormData();
		  //append data in dictionary format
		  formData.append('dafile', files[0], files[0].name);
		  formData.append('datext',commandstring.value);
		  formData.append('dafilename',files[0].name);
		  // Set up the request.
		  var xhr = new XMLHttpRequest();
		  //function called when state changes
          xhr.onreadystatechange = function() {
			//if request completed successfully and response received 
		    if (xhr.readyState === 4 && xhr.status === 200) {
			  if (commandstring.value=="Render")
			  {
				var stlmesh=MakeSTLMesh(xhr.responseText);
				scene.remove(parent);
				parent = new THREE.Object3D();
				parent.add(stlmesh);
				scene.add(parent);
			  }
			}
		  }
		  // Open the connection.
		  xhr.open('POST', 'http://localhost:8000/', true);  
		  // Send the Data.
		  xhr.send(formData);
		}
		//3D window with THREE.js
		//scene storage container
		var parent;
		var container, stats;
			var camera, scene, renderer;
			var cube, plane;
			var startTime	= Date.now();
			var targetRotation = 0;
			var targetRotationOnMouseDown = 0;
			var mouseX = 0;
			var mouseXOnMouseDown = 0;
			var windowHalfX = window.innerWidth / 2;
			var windowHalfY = window.innerHeight / 2;
			init();
			animate();
			//this gets called once
			function init() {
				// create the camera
				camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 1000 );
				camera.position.y = 350;
				camera.position.z = 350;
				camera.position.x=350;
		    	camera.lookAt(new THREE.Vector3(0,0,0));
				// create the Scene
				scene = new THREE.Scene();
				//add some lights			
				light1 = new THREE.DirectionalLight('white', 1.0);
				light1.position.set(200,200,200);
				light1.name = 'Back light';
				scene.add(light1);
				light2 = new THREE.DirectionalLight('white', 1.0);
				light2.position.set(-200,-200,-200);
				light2.name = 'Back light';
				scene.add(light2);
				light3 = new THREE.DirectionalLight('white', 1.0);
				light3.position.set(0,0,-200);
				light3.name = 'Back light';
				scene.add(light3);
				light4 = new THREE.DirectionalLight('white', 1.0);
				light4.position.set(0,0,200);
				light4.name = 'Back light';
				scene.add(light4);
				// create the container element
				container = document.createElement( 'div' );
				document.body.appendChild( container );
				// init the WebGL renderer and append it to the DOM
				renderer = new THREE.WebGLRenderer();
				renderer.setSize( window.innerWidth, window.innerHeight );
				container.appendChild( renderer.domElement );
				//add mouse controls to rotate camera around object
				controls = new THREE.TrackballControls(camera, renderer.domElement);
				controls.minDistance = 100;
				controls.maxDistance = 50000;
				//3d object will be stored here
				parent = new THREE.Object3D();
				scene.add(parent);
			}
			/**
			 * animate and display the scene
			*/
			function animate() {
				// render the 3D scene
				render();
				// relaunch the 'timer' 
				requestAnimationFrame( animate );
				controls.update();
			}
			/**
			 * Render the 3D scene
			*/
			function render() {
				// actually display the scene in the Dom element
				renderer.render( scene, camera );
			}
			//make mesh from string triangulation sent back from server
			function MakeSTLMesh(mySTLString)
			{
				var aloader= new THREE.STLLoader();
				var color1=new THREE.Color(0.99, 0.99, 0.99);
				var mygeom=aloader.parse(mySTLString);
				var material1 = new THREE.MeshLambertMaterial({
				ambient: color1,
				color: color1,
				transparent: true
				});
				var mymesh = new THREE.Mesh(mygeom, material1);
				mymesh.position.set(0,0,0);
				return mymesh;				
			}
					
		</script>
	</form>
	<!-- this is where the 3D view will be-->
	<!--<div id="viewport"></div>-->
</body>
We hope you find this tutorial useful. Contact us if you would like to hire us to create a CAD server for you.

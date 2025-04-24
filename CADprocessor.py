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
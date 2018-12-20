import time
import socket
import math
import opcua
from opcua import ua
from datetime import datetime

def AddPropertyVars(idx, parentNode, totVarSets):
    for i in range(0, totVarSets):
        currTime = datetime.now()
        parentNode.add_variable(idx, "VariableDbl"+"_"+str(i), tNodes, ua.VariantType.Double )
        parentNode.add_variable(idx, "VariableInt"+"_"+str(i), tNodes, ua.VariantType.Int16 )
        parentNode.add_variable(idx, "VariableStr"+"_"+str(i), tNodes, ua.VariantType.String )
        parentNode.add_variable(idx, "VariableTimeStamp"+"_"+str(i), currTime, ua.VariantType.DateTime)


def AddRootNode(idx, rootNode, baseName, totNodes, totDepth, totPropSets, currDepth):
    currDepth = currDepth + 1
    if currDepth <= totDepth:
        for i in range(0, totNodes):
            if currDepth == totDepth:
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSets)
            else:
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSets)
                AddRootNode(idx, groot, baseName, totNodes, totDepth, totPropSets, currDepth)  



if __name__ == "__main__":

    # setup our server
    server = opcua.Server()
    server.set_server_name("KTreeServer")
    server.set_application_uri("urn:" + socket.gethostname() + ":KTreeServer")
    server.set_endpoint("opc.tcp://localhost:4845")

    # setup our own namespace
    uri = "http://opcfoundation.org/UA/KTreeServer/"
    idx = server.register_namespace(uri)


    # get objects folder
    objects = server.get_objects_node()

    # starting!
    server.start()
    
    try:
        # run robot simulation
        tNodes = 5
        tDepth = 5
        tPropSets = 1

        groot = objects.add_object(idx,"Groot")
        groot.add_variable(idx, "Nodes per branch", tNodes, ua.VariantType.Int16 )
        groot.add_variable(idx, "Tree depth", tDepth, ua.VariantType.Int16 )
        groot.add_variable(idx, "Property sets", tPropSets, ua.VariantType.Int16 )
        groot_currenttime = groot.add_variable(idx, "CurrentTime", datetime.now(), ua.VariantType.DateTime)

        print("Building Server Hierarchy...sample change in progress")
        AddRootNode(idx, objects, "N", tNodes, tDepth, tPropSets, 0)      
        print("Hierarchy Tree Built")  

        while True:
            time.sleep(1)
            groot_currenttime.set_data_value(datetime.now(), ua.VariantType.DateTime)

    finally:
        #close connection, remove subcsriptions, etc
        server.stop()


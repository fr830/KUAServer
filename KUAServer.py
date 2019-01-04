import time
import socket
import math
import opcua
from opcua import ua
from datetime import datetime

def AddPropertyVars(idx, parentNode, totVarSets):
    
    for i in range(1, totVarSets+1):
        AddToNodeCount(3)
        parentNode.add_variable(idx, "VariableDbl"+"_"+str(i), tNodes, ua.VariantType.Double )
        parentNode.add_variable(idx, "VariableInt"+"_"+str(i), tNodes, ua.VariantType.Int16 )
        parentNode.add_variable(idx, "VariableStr"+"_"+str(i), tNodes, ua.VariantType.String )
        

def AddRootNode(idx, rootNode, baseName, totNodes, totDepth, totPropSets, currDepth):
    currDepth = currDepth + 1
    if currDepth <= totDepth:
        AddToNodeCount(totNodes)
        for i in range(1, totNodes+1):
            if currDepth == totDepth:
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSets)
            else:
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSets)
                AddRootNode(idx, groot, baseName, totNodes, totDepth, totPropSets, currDepth)


def AddToNodeCount(nAdds):
    tnods = groot_totalnodes.get_data_value()
    currNodeCount = tnods.Value.Value
    totNodeCount = nAdds + currNodeCount
    groot_totalnodes.set_data_value(totNodeCount, ua.VariantType.UInt32)


if __name__ == "__main__":

    # setup our server
    server = opcua.Server()
    server.set_server_name("KUAServer")
    server.set_application_uri("urn:" + socket.gethostname() + ":KUAServer")
    server.set_endpoint("opc.tcp://172.16.10.62:4846")

    # setup our own namespace
    uri = "http://opcfoundation.org/UA/KUAServer/"
    idx = server.register_namespace(uri)


    # get objects folder
    objects = server.get_objects_node()

    # starting!
    server.start()
    
    try:
        # run robot simulation
        tNodes = 3
        tDepth = 4
        tPropSets = 1

        groot = objects.add_object(idx,"Groot")
        groot.add_variable(idx, "Nodes per branch", tNodes, ua.VariantType.Int16 )
        groot.add_variable(idx, "Tree depth", tDepth, ua.VariantType.Int16 )
        groot.add_variable(idx, "Property sets", tPropSets, ua.VariantType.Int16 )
        groot_totalnodes = groot.add_variable(idx, "Total Nodes", tPropSets, ua.VariantType.Int32 )
        groot_currenttime = groot.add_variable(idx, "CurrentTime", datetime.now(), ua.VariantType.DateTime)

        groot_totalnodes.set_data_value(0, ua.VariantType.UInt32)
        print("Building Server Hierarchy, may connect while constructing...")
        AddRootNode(idx, groot, "PYNode", tNodes, tDepth, tPropSets, 0)

        numNodesTotal = groot_totalnodes.get_data_value().Value.Value
        print("Hierarchy Complete : Total Nodes :", numNodesTotal)


        while True:
            time.sleep(1)
            groot_currenttime.set_data_value(datetime.now(), ua.VariantType.DateTime)

    finally:
        #close connection, remove subcsriptions, etc
        server.stop()


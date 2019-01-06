import time
import socket
import math
import opcua
from opcua import ua
from datetime import datetime

def AddPropertyVars(idx, parentNode, totVarSets):
    
    for i in range(1, totVarSets+1):
        AddToNodeCount(6)
        parentNode.add_variable(idx, "VariableDbl"+"_"+str(i), tNodes, ua.VariantType.Double )
        parentNode.add_variable(idx, "VariableInt"+"_"+str(i), tNodes, ua.VariantType.Int16 )
        parentNode.add_variable(idx, "VariableStr"+"_"+str(i), tNodes, ua.VariantType.String )
        parentNode.add_property(idx, "PropertyString"+"_"+str(i), tNodes, ua.VariantType.String )
        parentNode.add_property(idx, "PropertyInt"+"_"+str(i), tNodes, ua.VariantType.Int16 )
        parentNode.add_property(idx, "PropertyDouble"+"_"+str(i), tNodes, ua.VariantType.Double )
        

def AddRootNode(idx, rootNode, baseName, totNodes, totNodesList, totDepth, totPropSets, totPropSetsList, currDepth):
    currDepth = currDepth + 1
    if currDepth <= totDepth:
        nodeCountAtDepth = totNodesList[currDepth-1]
        AddToNodeCount(nodeCountAtDepth)
        for i in range(1, nodeCountAtDepth+1):
            if currDepth == totDepth:
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSetsList[currDepth-1])
            else:
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSetsList[currDepth-1])
                AddRootNode(idx, groot, baseName, totNodes, totNodesList, totDepth, totPropSets, totPropSetsList, currDepth)


def AddToNodeCount(nAdds):
    tnods = groot_totalnodes.get_data_value()
    currNodeCount = tnods.Value.Value
    totNodeCount = nAdds + currNodeCount
    groot_totalnodes.set_data_value(totNodeCount, ua.VariantType.UInt32)


if __name__ == "__main__":

    # setup our server
    import socket    
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    IPAddr = "172.16.10.66"
    server = opcua.Server()
    server.set_server_name("KUAServer")
    server.set_application_uri("urn:" + socket.gethostname() + ":KUAServer")
    endPnt = "opc.tcp://"+IPAddr+":4846"
    print("EndPoint:", endPnt)
    server.set_endpoint(endPnt)

    # setup our own namespace
    uri = "http://opcfoundation.org/UA/KUAServer/"
    idx = server.register_namespace(uri)


    # get objects folder
    objects = server.get_objects_node()

    # starting!
    server.start()
    
    try:
        # run robot simulation
        tNodes = 7
        tDepth = 4
        tPropSets = 1

        tNodeArray = [3,10,4,6]
        tPropSetsArray = [5, 5, 5, 5]

        print("Building a ",tNodes, " Nodes By ",tDepth, " Depth By ",tPropSets, " Property Sets Config Hierarchy")

        groot = objects.add_object(idx,"Groot")
        groot.add_variable(idx, "Nodes per branch", tNodes, ua.VariantType.Int16 )
        groot.add_variable(idx, "Tree depth", tDepth, ua.VariantType.Int16 )
        groot.add_variable(idx, "Property sets", tPropSets, ua.VariantType.Int16 )
        groot_totalnodes = groot.add_variable(idx, "Total Nodes", tPropSets, ua.VariantType.Int32 )
        groot_currenttime = groot.add_variable(idx, "CurrentTime", datetime.now(), ua.VariantType.DateTime)

        groot_totalnodes.set_data_value(0, ua.VariantType.UInt32)
        print("Building Server Hierarchy, may connect while constructing...")
        AddRootNode(idx, groot, "PYNode", tNodes, tNodeArray, tDepth, tPropSets, tPropSetsArray, 0)

        numNodesTotal = groot_totalnodes.get_data_value().Value.Value
        print("Hierarchy Complete : Total Nodes :", numNodesTotal)


        while True:
            time.sleep(1)
            groot_currenttime.set_data_value(datetime.now(), ua.VariantType.DateTime)

    finally:
        #close connection, remove subcsriptions, etc
        server.stop()


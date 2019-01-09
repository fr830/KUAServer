import time
import socket
import math
import opcua
from opcua import ua
from datetime import datetime

def AddPropertyVars(idx, parentNode, totVarSets):
    
    for i in range(1, totVarSets+1):
        AddToNodeCount(6)
        v = parentNode.add_variable(idx, "VariableDbl"+"_"+str(i), 10.0, ua.VariantType.Double )
        v.add_property(idx, "unit", "double", ua.VariantType.String )
        
        v = parentNode.add_variable(idx, "VariableInt"+"_"+str(i), 10, ua.VariantType.Int16 )
        v.add_property(idx, "unit", "int", ua.VariantType.String )

        v = parentNode.add_variable(idx, "VariableStr"+"_"+str(i), "10", ua.VariantType.String )
        v.add_property(idx, "unit", "string", ua.VariantType.String )
        

def AddRootNode(idx, rootNode, baseName, totNodesList, totPropSetsList, currDepth):
    currDepth = currDepth + 1
    if currDepth <= len(totNodesList):
        nodeCountAtDepth = totNodesList[currDepth-1]
        AddToNodeCount(nodeCountAtDepth)
        for i in range(1, nodeCountAtDepth+1):
                groot = rootNode.add_object(idx, baseName+"_"+ str(currDepth) + "_" + str(i))
                AddPropertyVars(idx, groot, totPropSetsList[currDepth-1])
                AddRootNode(idx, groot, baseName, totNodesList, totPropSetsList, currDepth)


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
    #IPAddr = "172.16.10.66"
    IPAddr = "LocalHost"
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
        tNodeArray = [2,8,4,6]
        tPropSetsArray = [5, 5, 5, 5]

        groot = objects.add_object(idx,"Groot")
        groot_totalnodes = groot.add_variable(idx, "Total Nodes", 0, ua.VariantType.Int32 )

        groot_totalnodes.set_data_value(0, ua.VariantType.UInt32)
        print("Building Server Hierarchy, may connect while constructing...")
        AddRootNode(idx, groot, "PYNode", tNodeArray, tPropSetsArray, 0)

        AddToNodeCount(1)
        numNodesTotal = groot_totalnodes.get_data_value().Value.Value
        print("Hierarchy Complete : Total Nodes :", numNodesTotal)


        while True:
            time.sleep(1)

    finally:
        #close connection, remove subcsriptions, etc
        server.stop()


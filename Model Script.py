import struct
import os
from tkinter import filedialog as fd
import zlib
files = fd.askopenfilenames()
INVALID = False
verts = []
uvs   = []
norms = []
def strip2face(strip): #Credit goes to Turk695#0668 on Discord
    flipped = True
    tmpTable = []
    for x in range(len(strip)-2):
        if flipped:
            tmpTable.append((strip[x+1],strip[x+2],strip[x]))
        else:
            tmpTable.append((strip[x+2],strip[x+1],strip[x]))
        flipped = not flipped
    return tmpTable
for file in files:
    name = os.path.basename(file).split(".")[0]
    if not os.path.exists(os.getcwd()+"/OUTPUT/"+name+"/"):
        os.makedirs(os.getcwd()+"/OUTPUT/"+name+"/")
    outPath = os.getcwd()+"/OUTPUT/"+name+"/"
    with open(file, "rb") as f:
        fileString = f.read(4).decode("UTF-8")
        if fileString != "GATR":
            INVALID = True
            break
        headerInfo = struct.unpack('<IIIIIIIIIIHHIIIIIIIII',f.read(0x50))
        version = headerInfo[0]
        thing = headerInfo[1]
        thing2 = headerInfo[2]
        vertCount = headerInfo[3]
        triCount = headerInfo[4]
        meshCount = headerInfo[5]         #Just guessing here. Probably wrong.
        thing4 = headerInfo[6]
        extraObjectCount = headerInfo[7]  #This and boneCount might be flipped.
        boneCount = headerInfo[8]
        thing7 = headerInfo[9]
        thing8 = headerInfo[10]
        stringCount = headerInfo[11]
        startOfVerts = headerInfo[12]
        startOfTris = headerInfo[13]
        startOfUnknownTable1 = headerInfo[14]
        startOfUnknownTable2 = headerInfo[15]
        startOfUnknownTable3 = headerInfo[16]
        startOfUnknownTable4 = headerInfo[17]
        startOfUnknownTable5 = headerInfo[18]
        startOfStringTable = headerInfo[19]
        f.seek(startOfVerts)
        with open("mesh.obj", "w+") as o:
            for i in range(vertCount):
                vertInfo = struct.unpack('<fffIIffffffIffff',f.read(0x40))
                X_Location = vertInfo[0]*-1#Vertex coordinates (flip X so it matches how the game renders it)
                Y_Location = vertInfo[1]   
                Z_Location = vertInfo[2]
                Thing1 = vertInfo[3]       #No idea what these do. Might be the weight data for each vertex?
                Thing2 = vertInfo[4]
                X_Normal = vertInfo[5]     #Normals
                Y_Normal = vertInfo[6]
                Z_Normal = vertInfo[7]
                NRM = X_Normal*-1, Y_Normal, Z_Normal
                norms.append(NRM)
                X_Unknown= vertInfo[8]     #Could be rig-related
                Y_Unknown= vertInfo[9]
                Z_Unknown= vertInfo[10]
                Thing3 = vertInfo[11]      #Usually FFFFFFFF. No idea what it's for.
                X_UV1 = vertInfo[12]       #UVs. Handled weirdly, still working on them.
                Y_UV1 = vertInfo[13]
                UV = X_UV1, Y_UV1
                uvs.append(UV)
                X_UV2 = vertInfo[14]       #Repeats the same data
                Y_UV2 = vertInfo[15]
                A = str("v "+str(X_Location)+" "+str(Y_Location)+ " "+str(Z_Location)+"\n")
                o.write(A)
            for u in uvs:
                A = str("vt "+str(u[0])+" "+str(u[1])+"\n")
                o.write(A)
            for normal in norms:
                A = str("vn "+str(normal[0])+" "+str(normal[1])+ " "+str(normal[2])+"\n")
                o.write(A)
            f.seek(startOfTris)
            for i in range(1):
                D = "<"
                strips = []
                for i in range(int(triCount)):
                    D = D+"H"
                    triInfo = struct.unpack("<HHH",f.read(6))
                    strips.append(triInfo)
                    f.seek(-4,1)
                for strip in strips:
                    tris = strip2face(strip)
                    #print(tris)
                    for tri in tris:
                        A = str("f "+str(tri[0]+1)+"/"+str(tri[0]+1)+ "/"+str(tri[0]+1)+" "+str(tri[1]+1)+"/"+str(tri[1]+1)+ "/"+str(tri[1]+1)+" "+str(tri[2]+1)+"/"+str(tri[2]+1)+ "/"+str(tri[2]+1)+"\n")
                        o.write(A)
                    
                        

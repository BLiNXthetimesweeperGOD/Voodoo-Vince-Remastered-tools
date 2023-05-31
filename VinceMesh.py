import struct
import os
from tkinter import filedialog as fd
files = fd.askopenfilenames()
INVALID = False
verts = []
uvs   = []
norms = []
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
        tstrip_count = headerInfo[5]
        thing4 = headerInfo[6]
        extraObjectCount = headerInfo[7]  #This and boneCount might be flipped.
        boneCount = headerInfo[8]
        thing7 = headerInfo[9]
        thing8 = headerInfo[10]
        stringCount = headerInfo[11]
        startOfVerts = headerInfo[12]
        startOfTris = headerInfo[13]
        tstrip_table = headerInfo[14]
        startOfUnknownTable2 = headerInfo[15]
        startOfUnknownTable3 = headerInfo[16]
        startOfUnknownTable4 = headerInfo[17]
        startOfUnknownTable5 = headerInfo[18]
        startOfStringTable = headerInfo[19]
        f.seek(startOfVerts)
        with open(outPath+"mesh.obj", "w+") as o:
            for i in range(vertCount):
                vertInfo = struct.unpack('<fffIIffffffIffff',f.read(0x40))
                # tbh i dont think you should be flipping the x location or the normals but thats my take

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
                # FF FF FF FF normally means RGBA (vertex colours) but it can also be for weights
                X_UV1 = vertInfo[12]       #UVs. Handled weirdly, still working on them.
                Y_UV1 = vertInfo[13]
                # youll have to look for a value that says the scale of the uvs normally
                X_UV1 *= 6  # for this model it might be * 6 but for others it may be different
                Y_UV1 *= 6
                # for most model formats youll have to flip the y uv axis
                UV = X_UV1, (Y_UV1 * -1) + 1
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
            f.seek(tstrip_table)
            strip_counts = []
            for _ in range(tstrip_count):  # _ means we dont assign to any value
                strip_counts.append(struct.unpack('<I', f.read(4))[0])
                # this always returns a list aka one of these [0, 1, 2] or [1, ]
                # we only want the value and not the list so we get the first thing in the list with list[0]
                f.seek(48-4, 1)
            f.seek(startOfTris)
            face_list = []
            for face_count in strip_counts:
                strip = struct.unpack('<' + str(face_count) + 'H', f.read(2 * face_count))
                # the winding order was the wrong way :sunglasses: (the way the triangle strips be facing)
                for face in range(face_count - 2):
                    f1, f2, f3 = \
                        strip[(face + 0)], \
                        strip[(face + 1)], \
                        strip[(face + 2)]
                    if face & 1:
                        face_list.append((f1, f2, f3))
                    else:
                        face_list.append((f2, f1, f3))

            for tri in face_list:
                A = str("f "+str(tri[0]+1)+"/"+str(tri[0]+1)+ "/"+str(tri[0]+1)+" "+str(tri[1]+1)+"/"+str(tri[1]+1)+ "/"+str(tri[1]+1)+" "+str(tri[2]+1)+"/"+str(tri[2]+1)+ "/"+str(tri[2]+1)+"\n")
                o.write(A)

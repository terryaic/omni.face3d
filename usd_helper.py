import omni
from pxr import Usd, UsdLux, UsdGeom, UsdShade, Sdf, Gf, Vt
import struct

stage = omni.usd.get_context().get_stage()

def generate_prim(path, vecs):
    mesh = UsdGeom.Mesh.Define(stage, path)
    # Fill in VtArrays
    points = []
    normals = []
    indices = []
    vertexCounts = []

    cc = 0
    for i in range(len(vecs)):
        #subset = UsdGeom.Subset.Define(stage, path + "/subset" + str(i))
        #subset.CreateElementTypeAttr().Set("face")
        #subset_indices = [i]
        #rel = subset.GetPrim().CreateRelationship("material:binding", False)
        #rel.SetTargets([Sdf.Path(material_scope_path + "/OmniPBR" + str(i))])
        positions = vecs[i]
        for j in range(len(positions)):
            gf = Gf.Vec3f(positions[j][0], positions[j][1], positions[j][2])
            points.append(gf)
            normals.append(gf.GetNormalized())
            indices.append(cc)
            cc += 1
            
        #subset.CreateIndicesAttr().Set(subset_indices)
        vertexCounts.append(len(vecs))

    mesh.CreateFaceVertexCountsAttr().Set(vertexCounts)
    mesh.CreateFaceVertexIndicesAttr().Set(indices)
    mesh.CreatePointsAttr().Set(points)
    mesh.CreateDoubleSidedAttr().Set(False)
    mesh.CreateNormalsAttr().Set(normals)

def read_data(datafile):
    import carb
    ret = []
    with open(datafile, 'rb') as fp:
        n = struct.unpack('i', fp.read(4))[0]
        for i in range(1000):
            strands_len = struct.unpack('i', fp.read(4))[0]
            positions = []
            for j in range(strands_len):
                x,y,z = struct.unpack('fff', fp.read(12))
                #y = struct.unpack('f', fp.read(4))
                #z = struct.unpack('f', fp.read(4))
                positions.append([x*100,y*100,z*100])
            ret.append(positions)
    return ret

def convert_usd(datafile, usdfile):
    # set up axis to z
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1)

    defaultPrimPath = str(stage.GetDefaultPrim().GetPath())# Triangle mesh with multiple materials
    path = defaultPrimPath + "/triangleMesh"

    vecs = read_data(datafile)

    generate_prim(path, vecs)

convert_usd("strands00001.data", "strands00001.usd")
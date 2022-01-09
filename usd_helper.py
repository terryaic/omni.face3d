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
        subset = UsdGeom.Subset.Define(stage, path + "/subset" + str(i))
        subset.CreateElementTypeAttr().Set("face")
        subset_indices = [i]
        #rel = subset.GetPrim().CreateRelationship("material:binding", False)
        #rel.SetTargets([Sdf.Path(material_scope_path + "/OmniPBR" + str(i))])
        positions = vecs[i]
        for j in range(len(positions)):
            gf = Gf.Vec3f(positions[j][0], positions[j][1], positions[j][2])
            points.append(gf)
            normals.append(gf.Normalized())
            indices.append(cc)
            cc += 1
            
        subset.CreateIndicesAttr().Set(subset_indices)
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
        n = struct.unpack('i', fp.read(4))
        for i in range(n):
            strands_len = struct.unpack('i', fp.read(4))
            positions = []
            for j in range(strands_len):
                x = struct.unpack('f', fp.read(4))
                y = struct.unpack('f', fp.read(4))
                z = struct.unpack('f', fp.read(4))
                carb.log_info(x,y,z)
                positions.append([x,y,z])
            ret.append(positions)
    return ret

def convert_usd(datafile, usdfile):
    # set up axis to z
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 0.01)

    defaultPrimPath = str(stage.GetDefaultPrim().GetPath())# Triangle mesh with multiple materials
    path = defaultPrimPath + "/triangleMesh"

    vecs = read_data(datafile)

    generate_prim(path, vecs)

convert_usd("C:\\Users\\terry\\Documents\\Datasets\\strands00001.data", "C:\\Users\\terry\\Documents\\Datasets\\strands00001.usd")
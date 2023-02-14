from importlib import reload
import mesh, boundary
reload(mesh)
reload(boundary)
from mesh import *
from boundary import *

# Development story
m1 = MeshCylindrical1D(10, 1.0)
m2 = MeshCylindrical2D(10, 5, 1.0, 1.0)
# TBD: call all mesh functions
# Could create some of the meshes

# lesson: specified types in fuctions considered as hint by python
bc = BoundaryCondition1D(m2)
M, rhs = boundaryCondition1D(bc)
print(M)
print(rhs)



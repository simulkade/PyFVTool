import unittest
from pyfvtool import *
import numpy as np
from scipy.special import erf

def T_analytical_dirichlet(x,t, alfa, T0, Ts):
        return (T0-Ts)*erf(x/np.sqrt(4*alfa*t))+Ts

def T_analytical_neuman(x,t, alfa, T0, k, qs):
    return T0+qs/k*np.sqrt(4*alfa*t/np.pi)*np.exp(-x**2/(4*alfa*t))-qs/k*x*(1-erf(x/np.sqrt(4*alfa*t)))

def T_numerical(left_bc: str) -> float:
    L = 1.0 # [m] domain length
    k = 20.0 # 0.6 for water, 0.025 for air W/m/K
    rho = 8000.0 # kg/m^3
    c = 500.0 # J/kg/K (4200 for water, 1000 for air)
    alfa = k/(rho*c) # heat diffusion
    T0 = 300.0 # [K]
    Ts = 350.0 # [K]
    qs = 1000 # [W/m^2]
    t_sim = L**2/(20*alfa) # [s]
    time_steps = 50
    dt = t_sim/time_steps # 
    Nx = 50 # number of cells
    m = createMesh1D(Nx, L)
    # Boundary condition
    BC = createBC(m)
    if left_bc == "Dirichlet":
        BC.left.a[:] = 0.0
        BC.left.b[:] = 1.0
        BC.left.c[:] = Ts
        T_analytic = lambda x,t: T_analytical_dirichlet(x, t, alfa, T0, Ts)
    else:
        BC.left.a[:] = k
        BC.left.b[:] = 0.0
        BC.left.c[:] = -qs
        T_analytic = lambda x,t: T_analytical_neuman(x, t, alfa, T0, k, qs)

    # Initial condition
    T_init = createCellVariable(m, T0, BC) # initial condition
    # physical parameters
    alfa_cell = createCellVariable(m, alfa, createBC(m))
    alfa_face = harmonicMean(alfa_cell)

    M_diff = diffusionTerm(alfa_face)
    [M_bc, RHS_bc] = boundaryConditionTerm(BC)

    t=0
    while t<t_sim:
        t +=dt
        [M_trans, RHS_trans] = transientTerm(T_init, dt, 1.0)
        T_val = solvePDE(m, M_bc+M_trans-M_diff, RHS_bc+RHS_trans)
        T_init.update_value(T_val)

    x = m.facecenters.x
    T_face = linearMean(T_val)
    T_num = T_face.xvalue
    T_an = T_analytic(x, t_sim)
    er = np.sum(np.abs(T_num-T_an)/T_an)/Nx
    return er
     
class TestDiffusion(unittest.TestCase):
    def test_1d_dirichlet(self):
        print("\n Running 1D conduction heat transfer with Dirichlet boundary:")
        # code goes here
        # Parameters
        left_bc = "Dirichlet"
        er = T_numerical(left_bc)
        eps_T = 0.001
        self.assertLessEqual(er, eps_T)
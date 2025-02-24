"""
cylinder3d_unsteady ce test
"""

import paddlescience as psci
import numpy as np
import paddle

paddle.seed(1)
np.random.seed(1)

# paddle.enable_static()
paddle.disable_static()


# load real data
def GetRealPhyInfo(time, need_cord=False, need_physic=False):
    """
    get real phy_info
    """
    real_data = np.load("flow_unsteady_re200/flow_re200_" + str(time) + "_xyzuvwp.npy")
    real_data = real_data.astype(np.float32)
    if need_cord is False and need_physic is False:
        print("Error: you need to get cord or get physic infomation")
        exit()
    elif need_cord is True and need_physic is True:
        return real_data
    elif need_cord is True and need_physic is False:
        return real_data[:, 0:3]
    elif need_cord is False and need_physic is True:
        return real_data[:, 3:7]
    else:
        pass


# get init physic infomation
def GenInitPhyInfo(xyz):
    """
    get init_phy_info
    """
    uvw = np.zeros((len(xyz), 3)).astype(np.float32)
    length = len(xyz)
    for i in range(length):
        if abs(xyz[i][0] - (-8)) < 1e-4:
            uvw[i][0] = 1.0
    return uvw


# define start time and time step
start_time = 100
time_step = 1

cc = (0.0, 0.0)
cr = 0.5
geo = psci.geometry.CylinderInCube(origin=(-8, -8, -2), extent=(25, 8, 2), circle_center=cc, circle_radius=cr)

geo.add_boundary(name="left", criteria=lambda x, y, z: abs(x + 8.0) < 1e-4)
geo.add_boundary(name="right", criteria=lambda x, y, z: abs(x - 25.0) < 1e-4)
geo.add_boundary(name="circle", criteria=lambda x, y, z: ((x - cc[0]) ** 2 + (y - cc[1]) ** 2 - cr ** 2) < 1e-4)

# discretize geometry
geo_disc = geo.discretize(npoints=[100, 100, 4], method="uniform")

# the real_cord need to be added in geo_disc
real_cord = GetRealPhyInfo(start_time, need_cord=True)
geo_disc.user = real_cord

# N-S equation
pde = psci.pde.NavierStokes(nu=0.01, rho=1.0, dim=3, time_dependent=True, weight=[0.01, 0.01, 0.01, 0.01])

pde.set_time_interval([100.0, 110.0])

# boundary condition on left side: u=10, v=w=0
bc_left_u = psci.bc.Dirichlet("u", rhs=1.0, weight=1.0)
bc_left_v = psci.bc.Dirichlet("v", rhs=0.0, weight=1.0)
bc_left_w = psci.bc.Dirichlet("w", rhs=0.0, weight=1.0)

# boundary condition on right side: p=0
bc_right_p = psci.bc.Dirichlet("p", rhs=0.0, weight=1.0)

# boundary on circle
bc_circle_u = psci.bc.Dirichlet("u", rhs=0.0, weight=1.0)
bc_circle_v = psci.bc.Dirichlet("v", rhs=0.0, weight=1.0)
bc_circle_w = psci.bc.Dirichlet("w", rhs=0.0, weight=1.0)

# add bounday and boundary condition
pde.add_bc("left", bc_left_u, bc_left_v, bc_left_w)
pde.add_bc("right", bc_right_p)
pde.add_bc("circle", bc_circle_u, bc_circle_v, bc_circle_w)

# pde discretization
pde_disc = pde.discretize(time_method="implicit", time_step=time_step, geo_disc=geo_disc)

# Network
net = psci.network.FCNet(num_ins=3, num_outs=4, num_layers=10, hidden_size=50, activation="tanh")

# Loss
loss = psci.loss.L2(p=2)

# Algorithm
algo = psci.algorithm.PINNs(net=net, loss=loss)

# Optimizer
opt = psci.optimizer.Adam(learning_rate=0.001, parameters=net.parameters())

# Solver parameter
solver = psci.solver.Solver(pde=pde_disc, algo=algo, opt=opt)

# num_epoch in train
train_epoch = 2000

# Solver time: (100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]
num_time_step = 10
current_interior = np.zeros((len(pde_disc.geometry.interior), 3)).astype(np.float32)
current_user = GetRealPhyInfo(start_time, need_physic=True)[:, 0:3]
for i in range(num_time_step):
    next_time = start_time + (i + 1) * time_step
    print("############# train next time=%f train task ############" % next_time)
    solver.feed_data_interior_cur(current_interior)  # add u(n) interior
    solver.feed_data_user_cur(current_user)  # add u(n) user
    solver.feed_data_user_next(GetRealPhyInfo(next_time, need_physic=True))  # add u(n+1) user
    next_uvwp = solver.solve(num_epoch=train_epoch)
    # Save vtk
    file_path = "train_flow_unsteady_re200/fac3d_train_rslt_" + str(next_time)
    psci.visu.save_vtk(filename=file_path, geo_disc=pde_disc.geometry, data=next_uvwp)
    # next_info -> current_info
    next_interior = np.array(next_uvwp[0])
    next_user = np.array(next_uvwp[-1])
    current_interior = next_interior[:, 0:3]
    current_user = next_user[:, 0:3]

from ase.io.trajectory import TrajectoryReader
from electrolens import view

traj = TrajectoryReader("../../water_data.traj")
view(traj)
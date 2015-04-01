from matplotlib import patches
import matplotlib.pyplot as plt
import numpy as np
import sys
from bifurcate import Drawing, draw

test_data = (
    (3, 2, 5, (
        (2, 2, 2, ()),
        (1, 2, -2, ())
    )),
    (6, 2, -2, (
        (3,2,+1.5,()),
        (3,2,-4,()),
    ))
)

d = Drawing()
draw(d, 0, 0, 0, 10, 0, 0, test_data)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylim(-20,20)
ax.set_xlim(-20,20)
patch = patches.PathPatch(d.path(), facecolor='none', lw=2)
ax.add_patch(patch)
plt.savefig('bah.png')

mat = np.load('haplotypes.npy')
sys.setrecursionlimit(a.shape[0])
#First dim is variants

root = ()

for i in range(mat.shape)


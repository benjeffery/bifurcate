from collections import namedtuple
from matplotlib import patches
import matplotlib.pyplot as plt
import numpy as np
import sys
from bifurcate import Tree, Node
from drawing import Drawing, draw
import pprint

mat = np.load('haplotypes.npy')
pos = np.load('pos.npy')
mat = mat[:50,:]
tree = Tree(mat, pos)
tree.arrange_y(0.2, 10)
d = Drawing(facecolor='none', edgecolor='grey', joinstyle="round", antialiased=True)
draw(d, 0, 0, 0, float(mat.shape[1])/5, 0, 0, [tree.root_node])

fig = plt.figure(figsize=(24,12), dpi=800)
ax = fig.add_subplot(111)
ax.set_xlim(0, 4000)
ax.set_ylim(-1000, 1000)
for patch in d.patches:
    ax.add_patch(patch)
plt.show()
plt.savefig('bah.png')
plt.savefig('bah.eps')
print(tree)

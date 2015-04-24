from collections import namedtuple
from matplotlib import patches
import matplotlib.pyplot as plt
import numpy as np
import sys
from bifurcate import Tree, Node
from drawing import Drawing
import pprint

mat = np.load('haplotypes.npy')
pos = np.load('pos.npy')
mat = mat[:100,:]
tree = Tree(mat, pos)
sample_size = 0.2
tree.arrange_y(sample_size, 10)
d = Drawing(facecolor='grey', alpha = .2, capstyle='round', joinstyle="round", antialiased=True)
tree.draw(d, 0, 0, sample_size)

fig = plt.figure(figsize=(24,12))
ax = fig.add_subplot(111)
ax.set_xlim(0, 4000)
ax.set_ylim(-2000, 2000)
for patch in d.patches:
    ax.add_patch(patch)
plt.show()
plt.savefig('bah.png')
plt.savefig('bah.eps')
print(tree)

from collections import namedtuple
from matplotlib import patches
import matplotlib.pyplot as plt
import numpy as np
import sys
from bifurcate import Drawing, draw, tree, Node
import pprint

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

#w,x,y,children

test_data = (
    Node(3, (
        Node(2, (), 1, 2),
        Node(1, (), 1, -2)
    ), 1, 5),
    Node(6, (
        Node(3, (), 1, 1.5),
        Node(3, (), 1, -4)
    ), 1, -2)
)



#d = Drawing()
#draw(d, 0, 0, 0, 10, 0, 0, test_data)


mat = np.load('haplotypes.npy')[:500, :]
print(mat)
print(mat.shape)

tree = tree(mat)
d = Drawing(facecolor='black', lw=0.5)
draw(d, 0, 0, 0, float(mat.shape[1])/20, 0, 0, tree)

fig = plt.figure(figsize=(12,6), dpi=800)
ax = fig.add_subplot(111)
ax.set_ylim(-2000, 2000)
ax.set_xlim(0, 8000)
for patch in d.patches:
    ax.add_patch(patch)
plt.savefig('bah.png')
plt.savefig('bah.svg')
print(tree)

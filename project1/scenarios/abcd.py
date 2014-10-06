import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:
    h1a    s4--s5    h2a
       \  /      \  /
        s1        s2
       /  \      /  \ 
    h1b    --s3--    h2b
    """

    switch_type.create('A')
    switch_type.create('B')
    switch_type.create('C')
    switch_type.create('D')

    host_type.create('ha')
    host_type.create('hb')
    host_type.create('hc')
    host_type.create('hd')

    topo.link(A, ha)
    topo.link(B, hb)
    topo.link(C, hc)
    topo.link(D, hd)

    topo.link(A, B, 1)
    topo.link(A, C, 1)
    topo.link(B, D, 1)
    topo.link(C, D, 10)
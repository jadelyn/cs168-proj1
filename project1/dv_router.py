from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        self.forwarding_table = {} # router to latency
        self.neighbors = {} # neighbors to port
        self.first_hops = {} # destinations to the neighbor on the shortest path
        self.changed = False

    def send_routing_update(self):
        update = RoutingUpdate()
        for neighbor in self.neighbors.keys():
        	update.add_destination(neighbor, self.forwarding_table[neighbor])
        for neighbor in self.neighbors.keys():
        	self.send(update, self.neighbors[neighbor], False)
        return None

    def handle_rx (self, packet, port):
        if type(packet) is DiscoveryPacket:
        	if packet.is_link_up:
        		self.neighbors[packet.src] = port
        		self.forwarding_table[packet.src] = packet.latency
        		self.first_hops[packet.src] = packet.src
        	else:
        		del self.neighbors[packet.src]
        		self.forwarding_table[packet.src] = float("inf")
        		for destination in self.first_hops.keys():
        			if self.first_hops[destination] == packet.src:
        				self.first_hops[destination] = None

        	self.send_routing_update()



        elif type(packet) is RoutingUpdate:
        	dests = packet.all_dests()
        	for dest in dests:
        		if self == dest:
        			continue
        		if not packet.src in self.forwarding_table:
        			self.forwarding_table[packet.src] = float("inf")
        		if not dest in self.forwarding_table:
        			self.forwarding_table[dest] = float("inf")
        		if not dest in self.first_hops:
        			self.first_hops[dest] = None
        		new_distance = self.forwarding_table[packet.src] + packet.get_distance(dest)
        		if self.forwarding_table[dest] > new_distance:
        			self.forwarding_table[dest] = new_distance
        			self.first_hops[dest] = packet.src
        			self.changed = True
        	if self.changed:
        		self.send_routing_update()
        		self.changed = False






    def print_info(self):
        print("This switch :" + self.name)
        print("This switch's forwarding_table:")
        for key in self.forwarding_table.keys():
        	print("   Router:" + key.name + "  Distance:" + str(self.forwarding_table[key]))
        
        print("This switch's neighbors:")
        for key in self.neighbors.keys():
        	print("   Router:" + key.name + "  Port:" + str(self.neighbors[key]))

        print("This switch's destinations/first hops:")
        for key in self.first_hops.keys():
        	print("   Destination:" + key.name + "  First Hop:" + self.first_hops[key].name)




            
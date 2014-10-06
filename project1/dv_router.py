from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        self.forwarding_table = {} # destinations to latency
        self.neighbors = {} # neighbors to port
        self.neighbor_forwarding_tables = {} # neighbors to neighbors' forwarding tables
        self.first_hops = {} # destinations to the neighbor on the shortest path
        #self.changed = False

    def send_routing_update(self):
        update = RoutingUpdate()
        for destination in self.first_hops.keys():
            update.add_destination(destination, self.forwarding_table[destination])
        for neighbor in self.neighbors.keys():
            self.send(update, self.neighbors[neighbor], False)
        return None

    def handle_rx (self, packet, port):
        if type(packet) is DiscoveryPacket:
            if packet.is_link_up:
                self.neighbors[packet.src] = port
                self.neighbor_forwarding_tables[packet.src] = {}
                
                if not packet.src in self.forwarding_table or self.forwarding_table[packet.src] > packet.latency:
                    self.forwarding_table[packet.src] = packet.latency
                    self.first_hops[packet.src] = packet.src

            else:
                del self.neighbors[packet.src]
                del self.neighbor_forwarding_tables[packet.src]
                self.forwarding_table[packet.src] = float("inf")
                for destination in self.first_hops.keys():
                    if self.first_hops[destination] == packet.src:
                        self.first_hops[destination] = None

            self.send_routing_update()


        elif type(packet) is RoutingUpdate:
            changed = False
            dests = packet.all_dests()
            neighbor_table = {}

            # if our neighbor isn't in our forwarding table
            if not packet.src in self.forwarding_table:
                self.forwarding_table[packet.src] = packet.get_distance(self)
                self.first_hops[packet.src] = packet.src

            # update our copy of the neighbor's forwarding table
            for dest in dests:
                neighbor_table[dest] = packet.get_distance(dest)
            self.neighbor_forwarding_tables[packet.src] = neighbor_table

            # update our own forwarding table if necessary
            for dest in dests:
                if self == dest:
                    continue
                if not dest in self.forwarding_table:
                    self.forwarding_table[dest] = self.forwarding_table[packet.src] + self.neighbor_forwarding_tables[packet.src][dest]
                if not dest in self.first_hops or self.first_hops[dest] == None:
                    self.first_hops[dest] = packet.src

                min_distance_neighbor = None
                min_distance = float("inf")
                for neighbor in self.neighbor_forwarding_tables.keys():
                    if not dest in self.neighbor_forwarding_tables[neighbor]:
                        self.neighbor_forwarding_tables[neighbor][dest] = float("inf")

                    dist_to_dest = self.neighbor_forwarding_tables[neighbor][dest] + self.forwarding_table[neighbor]
                    if dist_to_dest < min_distance:
                        min_distance = dist_to_dest
                        min_distance_neighbor = neighbor

                # if changed:
                if dist_to_dest != self.forwarding_table[dest] or min_distance_neighbor != self.first_hops[dest]:
                    self.forwarding_table[dest] = dist_to_dest
                    self.first_hops[dest] = min_distance_neighbor
                    changed = True




                """
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
                """
            if changed:
                self.send_routing_update()







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

        print("This switch's neighbors' forwarding tables:")
        for neighbor in self.neighbor_forwarding_tables.keys():
            print("   Neighbor:" + neighbor.name)
            for key in self.neighbor_forwarding_tables[neighbor].keys():
                print("       Router:" + key.name + "  Distance:" + str(self.neighbor_forwarding_tables[neighbor][key]))


            
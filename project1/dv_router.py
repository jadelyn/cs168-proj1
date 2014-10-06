from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        self.routing_table = {} # self or neighbor to distance vector (destination to distance)
        self.routing_table[self] = {self:0}
        self.neighbor_ports = {} # neighbor to port
        self.first_hops = {} # destination to first hop
        self.first_hops[self] = self
        self.link_latencies = {} # neighbor to link latencies

    def send_routing_update(self):
        for neighbor in self.neighbor_ports.keys():
            update = RoutingUpdate()
            for dest in self.routing_table[self].keys():
                if dest in self.first_hops.keys() and self.first_hops[dest] == neighbor and dest != neighbor:
                    update.add_destination(dest, 51)
                else:
                    update.add_destination(dest, self.routing_table[self][dest])
            self.send(update, self.neighbor_ports[neighbor], False)
        return None

    def handle_rx (self, packet, port):
        neighbor = packet.src
        updated = False
        if type(packet) is DiscoveryPacket:
            if packet.is_link_up:
                self.neighbor_ports[neighbor] = port
                self.link_latencies[neighbor] = packet.latency

                if not neighbor in self.routing_table[self] or self.routing_table[self][neighbor] > packet.latency:
                    self.routing_table[self][neighbor] = packet.latency
                    self.first_hops[neighbor] = neighbor
                    updated = True

            else:
                if neighbor in self.routing_table.keys():
                    del self.routing_table[neighbor]
                del self.neighbor_ports[neighbor]
                del self.link_latencies[neighbor]
       
                if self.first_hops[neighbor] == neighbor:
                    del self.first_hops[neighbor]
                    self.routing_table[self][neighbor] = 51
                    #del self.routing_table[self][neighbor]
                    updated = True

                for destination in self.first_hops.keys():
                    if self.first_hops[destination] == neighbor:
                        del self.first_hops[destination]
                        self.routing_table[self][destination] = 51
                        #del self.routing_table[self][destination]
                        updated = True

        elif type(packet) is RoutingUpdate:
            dests = packet.all_dests()
            
            # update our copy of the neighbor's distance vector
            self.routing_table[neighbor] = {}
            for dest in dests:
                self.routing_table[neighbor][dest] = packet.get_distance(dest)

            # update our own distance vector if necessary
            for dest in dests:
                if not dest in self.first_hops.keys() and self.routing_table[self][neighbor] < 51 and packet.get_distance(dest) < 51:
                    self.first_hops[dest] = neighbor
                    self.routing_table[self][dest] = packet.get_distance(dest) + self.routing_table[self][neighbor]
                    updated = True
                else:
                    distance_to_dest_through_neighbor = self.routing_table[neighbor][dest] + self.routing_table[self][neighbor]
                    if self.routing_table[neighbor][dest] >= 51:
                        if dest in self.first_hops.keys():
                            if self.first_hops[dest] == neighbor:
                                if dest in self.link_latencies.keys():
                                    self.routing_table[self][dest] = self.link_latencies[dest]
                                    self.first_hops[dest] = dest
                                    updated = True
                                else:
                                    self.routing_table[self][dest] = 51
                                    del self.first_hops[dest]
                                    updated = True

                    elif distance_to_dest_through_neighbor < self.routing_table[self][dest]:
                        self.routing_table[self][dest] = distance_to_dest_through_neighbor
                        self.first_hops[dest] = neighbor
                        updated = True
                    elif distance_to_dest_through_neighbor > self.routing_table[self][dest]:
                        if self.first_hops[dest] == neighbor:
                            self.routing_table[self][dest] = distance_to_dest_through_neighbor
                            updated = True
                    else:
                        if self.first_hops[dest] != neighbor:
                            if self.neighbor_ports[self.first_hops[dest]] > self.neighbor_ports[neighbor]:
                                self.first_hops[dest] = neighbor

        else:
            if packet.dst == self:
                return None
            if packet.dst in self.first_hops.keys():
                self.send(packet, self.neighbor_ports[self.first_hops[packet.dst]], False)
            


        if updated:
            self.send_routing_update()

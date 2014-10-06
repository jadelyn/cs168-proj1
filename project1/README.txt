My name: Kevin Hu
Partner's name: Jade Hua

Challenges: Handling links going down was difficult.

New feature: The routers can be improved by adding autonomous systems that contain certain routers under their control, and routers under the same system have information about each other but not routers outside its system. 

Our code can handle link weights by checking if a discovery packet's latency is greater than the old distance to the neighbor on the changed link, and if our first hop to the neighbor is the neighbor itself, then we update the distance of the neighbor to match the new latency as well as all destinations in our distance vector that have the neighbor as the first hop. 

If the discovery packet's latency is less than the old distance to the neighbor, and the first hop to that neighbor wasn't the neighbor itself, then we change the first hop to the neighbor to the neighbor itself and update our distance to the neighbor to the new latency. If the first hop was the neighbor itself, then we update all destinations in our distance vector that have the neighbor as the first hop to use the new latency instead of the old one. 

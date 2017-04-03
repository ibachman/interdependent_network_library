# Interdependent network library
This respository contains the necessary methods and classes to use interdependent networks with a consumer-supplier behaviour 
as presented in the [work of Parandehgheibi et al](http://ieeexplore.ieee.org/abstract/document/6831395/authors).Here the 
interacting networks considered are the logic Internet network (AS network) and the physical Internet network.

## Methods list
 * `create_from_csv`: Receives 3 .CSV files that represent the physical network, the AS network, and the interactions network. 
 It also receives a list of provider nodes identifiers (as specified on the .CSV) on each the physical and AS network. Each 
 .CSV file must contain pairs of nodes separated by comma that represent edges of the network. The node can have any name as 
 long as it is unique among both networks.
 * `create_from_graph`: Receives 3 igraph Graph() objects reprenting the physical network, the AS network, and the interactions 
 network (each graph must have a name attribute and the names must be unique among the physcial and AS network). It also receives
 a list of provider nodes identifiers (as specified on the graph's name attribute) on each the physical and AS network.
 * `attack_nodes`: Receives a list of nodes identifiers to remove. This method deletes the nodes in the given list and executes
 the cascading failure process as described by [Parandehgheibi et al](http://ieeexplore.ieee.org/abstract/document/6831395/authors).
 * `node_mtfr`: Returns the minimum amount of nodes to be removed to destroy the interactions network.
 * `get_ratio_of_functional_nodes_in_AS_network`: Returns the ratio of functional nodes in the AS network compared with the 
 initial state of the network. If no failure has occured (`attack_nodes` has not been used yet) it will return `1.0`. 
## Dependencies
 * igraph 

import igraph
import csv


def set_graph_from_csv(csv_file,graph=None):
    if graph is None:
        rename_map = {}
        k = 0
        names_list = []
        with open(csv_file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar=',')
            edge_list = []
            for row in reader:
                first = row[0]
                second = row[1]
                if first not in rename_map:
                    rename_map[first] = k
                    k += 1
                    names_list.append(first)
                if second not in rename_map:
                    rename_map[second] = k
                    k += 1
                    names_list.append(second)
                edge_list.append((rename_map[first], rename_map[second]))
        number_of_nodes = len(rename_map)
        graph = igraph.Graph()
        graph.add_vertices(number_of_nodes)
        graph.vs['name'] = names_list
        graph.add_edges(edge_list)
    else:
        with open(csv_file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar=',')
            for row in reader:
                first = row[0]
                second = row[1]
                graph.add_edge(first,second)
    return graph


class InterdependentGraph(object):

    def __init__(self):
        pass

    def create_from_csv(self,AS_net_csv, AS_provider_nodes, physical_net_csv, physical_provider_nodes,interactions_csv):
        # Create AS graph from csv file
        self.AS_network = set_graph_from_csv(AS_net_csv)
        # Create physical graph from csv file
        self.physical_network = set_graph_from_csv(physical_net_csv)
        # Create interactions graph from csv file. This contains the nodes of both networks
        self.interactions_network = igraph.Graph
        self.interactions_network = set_graph_from_csv(interactions_csv)
        as_net_name_list = self.AS_network.vs['name']
        physical_net_name_list = self.physical_network.vs['name']
        type_list = []
        for node in self.interactions_network.vs:
            if node['name'] in as_net_name_list:
                type_list.append(0)
            elif node['name'] in physical_net_name_list:
                type_list.append(1)
        self.interactions_network.vs['type'] = type_list
        # save provider nodes
        self.AS_providers = AS_provider_nodes
        self.physical_providers = physical_provider_nodes
        # save initial set of functional nodes
        self.initial_number_of_functional_nodes_in_AS_net = \
            len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0])
        return self

    def create_from_graph(self,AS_graph, AS_provider_nodes, physical_graph,physical_provider_nodes, interactions_graph):
        # save AS graph
        self.AS_network = AS_graph
        # save physical graph
        self.physical_network = physical_graph
        # prepare and save interactions graph
        self.interactions_network = interactions_graph
        as_net_name_list = self.AS_network.vs['name']
        physical_net_name_list = self.physical_network.vs['name']
        type_list = []
        for node in self.interactions_network.vs:
            if node['name'] in as_net_name_list:
                type_list.append(0)
            elif node['name'] in physical_net_name_list:
                type_list.append(1)
        self.interactions_network.vs['type'] = type_list
        # save provider nodes
        self.AS_providers = AS_provider_nodes
        self.physical_providers = physical_provider_nodes
        # save initial set of functional nodes
        self.initial_number_of_functional_nodes_in_AS_net = \
            len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0])
        return self

    def attack_nodes(self,list_of_nodes_to_delete):
        current_graph_A = self.AS_network
        current_graph_B = self.physical_network
        current_interaction_graph = self.interactions_network

        while True:
            # if there are no more nodes to delete, i.e, the network has stabilized, then stop
            if len(list_of_nodes_to_delete) == 0:
                break
            # Delete the nodes to delete on each network, including the interactions network
            nodes_to_delete_in_A = [node for node in list_of_nodes_to_delete if node in current_graph_A.vs['name']]
            nodes_to_delete_in_B = [node for node in list_of_nodes_to_delete if node in current_graph_B.vs['name']]
            current_graph_A.delete_vertices(nodes_to_delete_in_A)
            current_graph_B.delete_vertices(nodes_to_delete_in_B)
            current_interaction_graph.delete_vertices([n for n in list_of_nodes_to_delete if n in current_interaction_graph.vs['name']])

            # Determine all nodes that fail because they don't have connection to a provider
            nodes_without_connection_to_provider_in_A = set(range(len(current_graph_A.vs)))
            alive_nodes_in_A = current_graph_A.vs['name']
            for provider_node in self.AS_providers:
                if provider_node not in alive_nodes_in_A:
                    continue
                length_to_provider_in_network_A = current_graph_A.shortest_paths(provider_node)[0]
                zipped_list_A = zip(length_to_provider_in_network_A,range(len(current_graph_A.vs)))
                current_nodes_without_connection_to_provider_in_A = \
                    set([a[1] for a in zipped_list_A if a[0]==float('inf')])
                nodes_without_connection_to_provider_in_A = \
                    nodes_without_connection_to_provider_in_A\
                        .intersection(current_nodes_without_connection_to_provider_in_A)


            nodes_without_connection_to_provider_in_B = set(range(len(current_graph_B.vs)))
            alive_nodes_in_B = current_graph_B.vs['name']
            for provider_node in self.physical_providers:
                if provider_node not in alive_nodes_in_B:
                    continue
                print provider_node, "is alive"
                length_to_provider_in_network_B = current_graph_B.shortest_paths(provider_node)[0]
                zipped_list_B = zip(length_to_provider_in_network_B,range(len(current_graph_B.vs)))
                current_nodes_without_connection_to_provider_in_B = \
                    set([a[1] for a in zipped_list_B if a[0]==float('inf')])
                nodes_without_connection_to_provider_in_B = \
                    nodes_without_connection_to_provider_in_B\
                        .intersection(current_nodes_without_connection_to_provider_in_B)
            # save the names (unique identifier) of the nodes lost because can't access a provider
            names_of_nodes_lost_in_A = set(current_graph_A.vs(list(nodes_without_connection_to_provider_in_A))['name'])
            names_of_nodes_lost_in_B = set(current_graph_B.vs(list(nodes_without_connection_to_provider_in_B))['name'])
            # Delete all nodes that fail because they don't have connection to a provider on each network including
            # interactions network
            current_graph_A.delete_vertices(nodes_without_connection_to_provider_in_A)
            current_graph_B.delete_vertices(nodes_without_connection_to_provider_in_B)
            nodes_to_delete = list(names_of_nodes_lost_in_A.union(names_of_nodes_lost_in_B))
            current_interaction_graph.delete_vertices([n for n in nodes_to_delete if n in current_interaction_graph.vs['name']])
            # Get the nodes lost because they have lost all support from the other network
            zipped_list_interactions = zip(current_interaction_graph.degree(),current_interaction_graph.vs['name'])
            # Add them to the nodes to delete on the next iteration
            list_of_nodes_to_delete = [a[1] for a in zipped_list_interactions if a[0] < 1]

        return self

    def get_ratio_of_funtional_nodes_in_AS_network(self):
        functional_nodes_in_AS_net = len([a for a in self.AS_network.vs if self.AS_network.degree(a.index) > 0])
        return (functional_nodes_in_AS_net*1.0)/(self.initial_number_of_functional_nodes_in_AS_net*1.0)

    def node_mtfr(self):
        return len((self.interactions_network.maximum_bipartite_matching()).edges())








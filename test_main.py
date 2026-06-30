
#running tests to check the algo
import networkx as nx
from main import assign_darkness_cost


def test_lit_streets_have_np():
    #no penalty since tag lit = yes
    G = nx.MultiGraph()
    G.add_edge(1, 2, key=0, length=100, lit="yes")
    assign_darkness_cost(G)
    assert G[1][2][0]["cost"] == 100

def test_unlit_streets_get_penalized():
    # tag lit = no should have penalty 
    G = nx.MultiGraph()
    G.add_edge(1, 2, key=0, length=100, lit="no")
    assign_darkness_cost(G, darkness_penalty=3.0)
    assert G[1][2][0]["cost"] == 400  # 100 * (1 + 3.0)


def test_unknown_streets_get_milder_penalty():
    # no lighting data will have a penality applied 
    G = nx.MultiGraph()
    G.add_edge(1, 2, key=0, length=100, lit=None)
    assign_darkness_cost(G, unknown_penalty=1.0)
    assert G[1][2][0]["cost"] == 200  # 100 * (1 + 1.0)


def test_cost_defaults_to_length_one_if_missing():
    G = nx.MultiGraph()
    G.add_edge(1, 2, key=0, lit="yes")  # no length given
    assign_darkness_cost(G)
    assert G[1][2][0]["cost"] == 1


def test_best_lit_route_avoids_unlit_streets_when_possible():
    G = nx.MultiGraph()
    G.add_node(1, x=0, y=0)
    G.add_node(2, x=0, y=1)
    G.add_node(3, x=1, y=0)

    G.add_edge(1, 2, key=0, length=10, lit="no") #short but dark
    G.add_edge(1, 3, key=0, length=8, lit="yes")
    G.add_edge(3, 2, key=0, length=8, lit="yes")

    assign_darkness_cost(G, darkness_penalty=3.0, unknown_penalty=1.0)
    shortest_route = nx.shortest_path(G, 1, 2, weight="length")
    assert shortest_route == [1, 2]
    lit_route = nx.shortest_path(G, 1, 2, weight="cost")
    assert lit_route == [1, 3, 2]


def test_routes_are_valid_connected_paths():
    G = nx.MultiGraph()
    G.add_node(1, x=0, y=0)
    G.add_node(2, x=0, y=1)
    G.add_node(3, x=1, y=0)
    G.add_edge(1, 2, key=0, length=10, lit="no")
    G.add_edge(1, 3, key=0, length=8, lit="yes")
    G.add_edge(3, 2, key=0, length=8, lit="yes")
    assign_darkness_cost(G)

    lit_route = nx.shortest_path(G, 1, 2, weight="cost")

    #check every step in the route is a real edge in the graph
    for u, v in zip(lit_route[:-1], lit_route[1:]):
        assert G.has_edge(u, v), f"No edge between {u} and {v}, route is invalid"


if __name__ == "__main__":
    test_lit_streets_have_np()
    test_unlit_streets_get_penalized()
    test_unknown_streets_get_milder_penalty()
    test_cost_defaults_to_length_one_if_missing()
    test_best_lit_route_avoids_unlit_streets_when_possible()
    test_routes_are_valid_connected_paths()

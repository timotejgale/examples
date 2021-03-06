import pydot
graph = pydot.Dot('graphname', graph_type='digraph')
# pmo100 = pydot.Node("D")
pmo100 = pydot.Node('M', label='A', fillcolor='red', style='filled')
sa300 = pydot.Node("A")
sa100 = pydot.Node("B")
sa200 = pydot.Node("C")
sa200.set_style('filled')
sa200.set_fillcolor('green')
sa200.set_color('green')

graph.add_node(pmo100)
graph.add_edge(pydot.Edge(pmo100, sa300, arrowhead="normal", color='red'))
graph.add_edge(pydot.Edge(sa100, sa300, arrowhead="none"))
graph.add_edge(pydot.Edge(sa100, sa200))
graph.add_edge(pydot.Edge(pmo100, sa100))
sa200.set_fillcolor('red')
graph.write_png('example1_graph.png')
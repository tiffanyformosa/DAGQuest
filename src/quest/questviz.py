import graphviz

from .Quest import *

def viz(quest: Quest) -> graphviz.Digraph:
    dot = graphviz.Digraph(name=quest.name, comment=quest.description)
    for child, ancestors in quest._graph.items():
        edge_style = "solid" if child.required else "dotted"
        node_style = "filled" if child.hidden else ""
        dot.node(child.name, style=node_style)
        for anc in ancestors:
            dot.edge(anc.name, child.name, style=edge_style)
    return dot

if __name__ == "__main__":
    q1 = Objective("goal_1", "Do the first thing.")
    q2 = CollectionObjective("goal_2", 3, display_text="Collect [stop] trinkets.")
    q3 = Objective("goal_3", "Do the third thing.")
    q4 = Objective("goal_optional", "Do this if you wanna.", required=False)
    quest = Quest("Example Quest", "This is an example quest")
    quest.add(q3, q1, q2)
    quest.add(q2, q1)
    quest.add(q4, q1)
    quest.prepare()

    print(quest)
    print(quest.current)
    # Mark first quest objective complete.
    quest.objective("goal_1").mark_complete()
    quest.update()
    print(quest.current)
    quest.objective("goal_2").collect()
    quest.objective("goal_2").collect()
    print(quest.current)
    print(quest.completed)
    quest.objective("goal_2").collect()
    quest.objective("goal_optional").kill()
    quest.update()
    print(quest.current)
    quest.objective("goal_3").mark_complete()
    print(quest)

    viz(quest).render(directory='doctest-output', view=True)
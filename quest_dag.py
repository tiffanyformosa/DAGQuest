import graphlib

class Objective:

    FAIL = -1
    INPROGRESS = 0
    SUCCESS = 1

    def __init__(self,
                 name,
                 display_text="Do a thing.",
                 required=True):
        """
        :param name: Name of objective, used as key in Quest
        :param display_text: Display in quest log interface.
        :param required: Does this objective need to be completed?
        """
        self.name = name
        self.required = required
        self.display_text = display_text
        self.state = 0

    def mark_complete(self):
        """
        Mark this objective as complete.
        """
        self.state = Objective.SUCCESS

    def mark_failed(self):
        """
        Mark this objective as failed.
        """
        self.state = Objective.FAIL

    @property
    def completed(self) -> bool:
        """
        Check if this objective has been completed successfully.
        :return: Boolean value of success status.
        """
        return self.state == Objective.SUCCESS

    @property
    def failed(self):
        """
        Check if this objective has failed and cannot be completed.
        A failed objective blocks its successors in the quest.

        :return: Boolean value of success status.
        """
        return self.state == Objective.FAIL

    @property
    def in_progress(self):
        """
        Check if this objective is in progress.
        :return: Boolean value of state.
        """
        return self.state == Objective.INPROGRESS

    @property
    def status(self):
        """
        Return string representing current progress status.
        :return: Status string.
        """
        my_state = "Unknown"
        match self.state:
            case Objective.SUCCESS:
                my_state = "Success!"
            case Objective.FAIL:
                my_state = "Failed"
            case Objective.INPROGRESS:
                my_state = "In Progress"
        return my_state

    def __str__(self):
        return f"{self.display_text} [{self.status}]"

    def __repr__(self):
        is_opt = " [Optional]" if not self.required else ""
        return f"{self.name}: {self.display_text} [{self.status}]" + is_opt

class CollectionObjective(Objective):
    def __init__(self, name, start, stop=None, step=0, **kwargs):
        """
        Initialize a Collection objective, which counts up and down,
        mimicking the syntax of Python range().

        Syntax: CollectionObjective(name, start, stop, step)
        Also valid:
            CollectionObjective(name, stop)
            CollectionObjective(name, start, stop)
        :param name: Name of objective, used as key in quest,
        :param start: Start value. Default is 0.
        :param stop: Stop value. Required.
        :param step: Step value. Default: +/-1.
        :param kwargs: additional parameters passed to Objective.

        Special: To match RenPy formatting, a CollectionObjective's
        display_text takes [stop] and [start] and will replace them
        with the initialized values.
        """
        if stop is None:
            self.stop = int(start)
            self.start = 0
        else:
            self.start = int(start)
            self.stop = int(stop)
        if step == 0:
            if self.start < self.stop:
                self.step = 1
            else:
                self.step = -1
        else:
            self.step = int(step)

        self.has = self.start

        if "display_text" in kwargs.keys():
            kwargs["display_text"] = kwargs["display_text"].replace("[stop]", str(self.stop))
            kwargs["display_text"] = kwargs["display_text"].replace("[start]", str(self.start))

        super().__init__(name, **kwargs)

    def collect(self):
        """
        Increment an objective for a collection quest.
        :return: None
        """
        self.has += self.step
        if self.step > 0 and self.has >= self.stop:
            self.state = Objective.SUCCESS
        elif self.step < 0 and self.has <= self.stop:
            self.state = Objective.SUCCESS

    def empty(self):
        """
        Reset counter to start.
        :return:
        """
        self.has = self.start
        self.state = Objective.INPROGRESS

    @property
    def status(self):
        """
        Return string representing current progress status.
        :return: Status string.
        """
        my_state = f"{self.has}/{self.stop}"
        return my_state

class Quest:
    """
    Holds a graph of Objectives and uses a TopologicalSorter to handle them.
    """

    def __init__(self, name, graph=None):
        self.name = name
        self.current = []
        if graph is None:
            self._graph = {}
        else:
            self._graph = graph
        self._ts = graphlib.TopologicalSorter(graph)

    def add(self, objective, *predecessors):
        """
        :param objective: Add Objective to Quest
        :param predecessors: Add Required objectives to Quest
        :return:
        """
        # Split predecessors into required and optional
        reqs = [p for p in predecessors if p.required]
        opts = [p for p in predecessors if not p.required]

        # populate Graph with quest objectives
        self._graph.setdefault(objective, set()).update(reqs)
        #self._index.setdefault(objective.name, objective)
        for p in predecessors:
            self._graph.setdefault(p, set())
            #self._index.setdefault(p.name, p)

        # add objective and all optional goals to graph
        #self._ts.add(objective, *reqs)
        #for o in opts:
        #    self._ts.add(o)

    def objective(self, objective_name):
        return [c for c in self.current if c.name == objective_name][0]

    def update(self):
        """
        Progress the list of available quests.
        :return:
        """
        for c in self.current:
            if c.completed:
                #print(f"Completed {c}")
                self._ts.done(c)
                self.current.remove(c)
        self.current.extend(self._ts.get_ready())
        return self.current

    def prepare(self):
        self._ts = graphlib.TopologicalSorter(self._graph)
        self._ts.prepare()
        self.update()

    def __str__(self):
        tmp = graphlib.TopologicalSorter(self._graph)
        return str([*tmp.static_order()])

class Log:
    pass

if __name__ == "__main__":
    q1 = Objective("goal_1", "Do the first thing.")
    q2 = CollectionObjective("goal_2", 3, display_text="Collect [stop] trinkets.")
    print(q2.status)
    q3 = Objective("goal_3", "Do the third thing.")
    q4 = Objective("goal_optional", "Do this if you wanna.", required=False)
    quest = Quest("Example Quest")
    quest.add(q3, q1, q2)
    quest.add(q2, q1)
    quest.add(q4, q1)
    quest.prepare()

    print(quest)
    print(quest.current)
    # Mark first quest objective complete.
    quest.objective("goal_1").mark_complete()
    quest.update()
    print(quest)
    print(quest.current)
    print(quest._ts[0])
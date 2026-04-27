import graphlib

class Objective:

    FAIL = -1 # A failed branch cuts off progression.
    INPROGRESS = 0 # An in progress objective still needs to get done.
    SUCCESS = 1 # A successful objective was done!
    DEAD = 255 # A dead objective cannot be done, but allows the graph to progress.

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

    def mark_dead(self):
        """
        Mark this objective as dead.
        """
        self.state = Objective.DEAD

    kill = mark_dead

    def mark_failed(self):
        """
        Mark this objective as failed.
        """
        self.state = Objective.FAIL

    @property
    def done(self) -> bool:
        """
        Check if this objective has been completed, success or failure.
        :return: Boolean value of done status.
        """
        return self.state > 0

    @property
    def complete(self) -> bool:
        """
        Check if this objective was completed successfully.
        :return: Boolean value of success status.
        """
        return self.state == Objective.SUCCESS

    @property
    def failed(self) -> bool:
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
            case Objective.DEAD:
                my_state = "Dead"
        return my_state

    def __str__(self):
        return f"{self.display_text} [{self.status}]"

    def __repr__(self):
        is_opt = " [Optional]" if not self.required else ""
        return f"{self.name}: {self.display_text} [{self.status}]" + is_opt

class CollectionObjective(Objective):
    def __init__(self, name, start, stop=None, step=0, **kwargs):
        """
        Initialize a collection objective, which counts up and down,
        mimicking the syntax of Python range(), suitable for fetch quests.

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

class BranchObjective(Objective):
    """
    This is an objective that can end multiple different ways.
    """
    def __init__(self, name, endings, **kwargs):
        self.valid_states = endings
        if len(endings) >= Objective.DEAD:
            raise ValueError("Too many states! Raise Objective.DEAD or reduce endings.")
        super().__init__(name, **kwargs)

    def resolve(self, ending):
        """
        Set the status of this objective.
        :param ending:
        :return:
        """
        self.state = self.valid_states.index(ending) + 1

    @property
    def status(self):
        """
        Return string representing end state of this objective.
        :return: Status string
        """
        if self.state <= 0:
            return super().status
        else:
            return self.valid_states[self.state - 1]


class Quest:
    """
    Holds a graph of Objectives and uses a TopologicalSorter to handle them.
    """

    FAIL = -1
    INACTIVE = 0
    ACTIVE = 1
    COMPLETE = 2

    def __init__(self,
                 name,
                 description,
                 graph=None):
        self.name = name
        self.description = description
        self.current = set()
        self.status = Quest.INACTIVE
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

    def objective(self, objective_name) -> Objective:
        """
        Search current objectives by name
        :param objective_name: Name of objective to retrieve.
        :return: Objective.
        """
        return [c for c in self.current if c.name == objective_name][0]

    def update(self):
        """
        Progress the list of available quests.
        :return:
        """
        for c in self.current:
            if c.done:
                #print(f"Completed {c}")
                self._ts.done(c)
            elif c.failed:
                self.status = Quest.FAIL
                return None
        self.current = {c for c in self.current if not c.done}
        self.current.update(self._ts.get_ready())
        return self.current

    def prepare(self):
        """
        Set up the topological sorter; once this is done, the quest can be used.
        :return: None
        """
        self._ts = graphlib.TopologicalSorter(self._graph)
        self._ts.prepare()
        self.update()
        self.status = Quest.ACTIVE

    def _check_complete(self) -> bool:
        """
        Check if all goals remaining are optional: if yes, quest is complete.
        :return: If quest is complete.
        """
        self.update()
        to_do = [goal.required for goal in self.current]
        return not any(to_do)

    def complete(self) -> bool:
        """
        Attempt to end a quest, killing all remaining optional goals.
        :return: If quest can be turned in or not.
        """
        if self.status == Quest.COMPLETE:
            return True
        elif self._check_complete():
            # all goals remaining are optional. kill them.
            [goal.kill() for goal in self.current]
            self.update()
            self.status = Quest.COMPLETE
            return True
        else:
            return False

    def __str__(self):
        tmp = graphlib.TopologicalSorter(self._graph)
        return str([*tmp.static_order()])


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
    print(quest.current)
    quest.objective("goal_2").collect()
    quest.objective("goal_2").collect()
    print(quest.current)
    print(quest.complete())
    quest.objective("goal_2").collect()
    quest.objective("goal_optional").kill()
    quest.update()
    print(quest.current)
    quest.objective("goal_3").mark_complete()
    print(q1)


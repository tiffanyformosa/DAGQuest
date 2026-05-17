import graphlib

class Objective:
    """
    An objective is a step in a quest. A default objective is either
    complete or not complete; more complex objectives can call different methods
    to decide if they are complete or not.
    """
    FAIL = -1 # A failed branch cuts off progression.
    INPROGRESS = 0 # An in progress objective still needs to get done.
    SUCCESS = 1 # A successful objective was done!
    DEAD = 128 # A dead objective cannot be done, but allows the graph to progress.

    def __init__(self,
                 name,
                 display_text="Do a thing.",
                 required=True,
                 hidden=False):
        """
        :param name: Name of objective, used as key in Quest
        :param display_text: Display in quest log interface.
        :param required: Does this objective need to be completed?
        :param hidden: Is this objection visible? Used only in handlers.
        """
        self._name = name
        self._required = required
        self.hidden = hidden
        self._display_text = display_text
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
    def name(self) -> str:
        return self._name

    @property
    def required(self) -> bool:
        return self._required

    @property
    def display_text(self) -> str:
        return self._display_text

    @property
    def done(self) -> bool:
        """
        Check if this objective has been completed or killed
        :return: True if allows progression, otherwise false.
        """
        return self.state > Objective.INPROGRESS

    @property
    def success(self) -> bool:
        """
        Check if this objective was completed successfully.
        :return: True if success, False otherwise
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

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        is_opt = "(Optional) " if not self.required else ""
        return is_opt + f"{self.display_text} [{self.status}]"

    def __repr__(self):
        return f"{self.name}: " + str(self)

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
        # Deal with misplaced descriptions.
        if type(stop) is str:
            kwargs["display_text"] = stop
            stop = None
        elif type(step) is str:
            kwargs["display_text"] = step
            step = 0
        
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

    def collect(self, amount:int|None=None):
        """
        Increment an objective for a collection quest.
        
        :param amount: How much to add to the objective.
        :return: None
        """
        if amount is None:
            amount = self.step
        self.has += amount
        if self.step > 0 and self.has >= self.stop:
            self.mark_complete()
        elif self.step < 0 and self.has <= self.stop:
            self.mark_complete()

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

    def __iadd__(self, amount: int):
        """
        Collect increment wrapper.
        """
        self.collect(amount)

    def __isub__(self, amount: int):
        """
        Collect decrement wrapper.
        """
        self.collect(-amount)


class BranchObjective(Objective):
    """
    This is an objective that can end multiple different ways.

    Note: valid_states is 1-indexed since state 0 is in progress.
    """
    def __init__(self, name, endings: dict|list, default_text = "Choose a thing.", **kwargs):
        if len(endings) >= Objective.DEAD:
            raise ValueError("Too many states! Max {Objective.DEAD - 1} possible endings.")
        super().__init__(name, **kwargs)
        try:
            self.valid_states = ["in_progress"] + list(endings.keys())
            self._display_text = [endings.get(key, default_text) for key in self.valid_states]
        except TypeError:
            self.valid_states = ["in_progress"] + endings
            self._display_text = [default_text] + endings

    def resolve(self, state: str|int):
        """
        Set the status of this objective. Raises a ValueError if state is not in valid_states.
        :param state: Set state of ending within valid_states.
        :return:
        """
        if type(state) is int:
            if 0 <= state <= len(self.valid_states):
                self.state = state
        else:
            self.state = self.valid_states.index(state)

    @property
    def success(self):
        return 0 < self.state < len(self.valid_states)

    @property
    def status(self):
        """
        Return string representing end state of this objective.
        :return: Status string
        """
        if self.state <= 0 or self.state == Objective.DEAD:
            return super().status
        else:
            return self.valid_states[self.state]

    @property
    def display_text(self):
        """
        Return different display text depending on state.
        """
        return self._display_text[self.state]
        


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
        :param predecessors: Add Required Objectives to Quest
        :return:
        """
        reqs = []
        for p in predecessors:
            if isinstance(p, Objective):
                self._graph.setdefault(p, set())
            else:
                p = self.objective(p)
            
            if p.required: reqs.append(p)
        self._graph.setdefault(objective, set()).update(reqs)


    def objective(self, objective_name) -> Objective:
        """
        Search current objectives by name
        :param objective_name: Name of objective to retrieve. Keys are by necessary unique.
        :return: Objective.
        """
        if isinstance(objective_name, Objective):
            return objective_name
        else:
            return [c for c in self._graph if c.name == objective_name][0]
        """
        try:
            return [c for c in self.current if c.name == objective_name][0]
        except IndexError as e:
            return [c for c in self._graph if c.name == objective_name][0]
        """

    def is_active(self, objective_name) -> bool:
        """
        Check if Objective is active - useful for logic checking.
        
        :param objective_name: Name of objective to search for.
        """
        obj = self.objective(objective_name)
        return (obj.in_progress) and (obj in self.current) 

    def is_complete(self, objective_name) -> bool:
        """
        Wrapper to match syntax of is_active.
        :param objective_name: Name of objective to search for.
        """
        return self.objective(objective_name).done

    def one_hot(self, objective, heir):
        """
        When you declare an Objective as one-hot,
        you mark the objective complete and immediately kill
        all successor nodes except the heir.
        :param objective:
        :param heir:
        :return:
        """
        pass

    # Alias that's less comp-sci
    branch = one_hot

    def kill(self, objective):
        """
        When you kill a node, do the following:
        a) mark it dead
        b) self._ts.done()
        c) pop it from current
        d) get_ready()
        e) recursively kill all get-ready nodes.
        :param objective:
        :return:
        """
        pass


    def update(self):
        """
        Progress the list of available quests.
        :return:
        """
        # update: if a node is killed, kill all its children as well.
        # to make this compatible with kill,
        # need to call get_ready every time. 
        for c in self.current:
            if c.done:
                print(f"Completed {c}")
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
        finished = not any(to_do)
        #if finished:
        #    self.status = Quest.COMPLETE
        return finished


    def can_turn_in(self) -> bool:
        """
        Verify if quest can be completed.
        :return: If quest can be turned in or not.
        """
        if self.status == Quest.COMPLETE:
            # Cannot turn in a quest which is already complete.
            return False
        if not self._ts.is_active():
            return True
        else:
            return self._check_complete()

    def turn_in(self) -> bool:
        """
        Turn in a quest, marking it complete.
        """
        if self.can_turn_in():
            self.status = Quest.COMPLETE
            return True
        else:
            return False

    @property
    def completed(self) -> bool:
        return self.status == Quest.COMPLETE

    def summarize(self, show_all=False):
        """
        Expose static order of quest as generator.
        
        :param show_all: Show all objectives, or only completed + active objectives?
        """
        tmp = graphlib.TopologicalSorter(self._graph).static_order()
        for obj in tmp:
            if show_all or not obj.in_progress or (self.is_active(obj) and not obj.hidden):
                yield obj
    
    @property
    def state(self):
        """
        Quickly expose if anything major in quest has changed to avoid heavy recalculations.
        Byte must be 0 to 255, and we have 2 negative values possible so a small offset is added
        """
        keys = self._graph.keys()
        return bytes([k.state + k.hidden + self.status + 7 for k in keys])

    def __str__(self):
        tmp = graphlib.TopologicalSorter(self._graph)
        return str([*tmp.static_order()])


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
    print(quest.complete())
    quest.objective("goal_2").collect()
    quest.objective("goal_optional").kill()
    quest.update()
    print(quest.current)
    quest.objective("goal_3").mark_complete()
    print(quest)


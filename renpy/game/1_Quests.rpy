# You can initialize quest objectives in the order they should appear in the log.
label beans:
    python:
        tutorial_quest.add(Objective("talk_bob", "Talk to Bob."))
        tutorial_quest.add(CollectionObjective("beans", 10, "Collect 10 beans."), "talk_bob")
        tutorial_quest.add(Objective("give_beans", "Give the beans to Bob."), "talk_bob")
        tutorial_quest.add(
            BranchObjective(
                "give_bar",
                endings={
                    "Carol": "You gave the chocolate to Carol.",
                    "Dave": "You gave the chocolate to Dave.",
                    "Eat it.": "You ate all the chocolate yourself!"},
                default_text="Give the chocolate bar to either Carol or Dave.",
                required=False),
            "give_beans")
        tutorial_quest.add(Objective("get_password", "Get the password from Alice.", required=False, hidden=True))
        tutorial_quest.add(Objective("password", "Tell the password to Eileen.", hidden=True))
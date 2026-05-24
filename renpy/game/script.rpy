define a = Character("Alice")
define b = Character("Bob")
define c = Character("Carol")
define d = Character("Dave")
define e = Character("Eileen")
default knows_quest_basics = False
default knows_hidden_objective = False
default knows_password = False
default met_eileen = False

label start:
    show bg room
    show screen keymap_screen
    call beans
    call callback
    a "Hello! My name is Alice."
    a "I am here to provide a demo for how the {b}Quest{/b} module works in RenPy."
    a "First, let me assign you a {b}Quest{/b}."
    
    $ tutorial_quest.prepare()
    $ tutorial_entry.locked = False
    
    # jump main_quest
    
    a "You can keep track of your {b}Quest{/b}s in your quest log."
    a "The quest log is a RenPy Screen wrapping a stand-alone Python library."
    a "Access your quest log by pressing Q."
    a "Go on, try it."
    
    a "You can see you have been assigned a new {b}Quest{/b}."
    a "This {b}Quest{/b} will demonstrate different types of {b}Objective{/b}s in the module."

label quest_types:
    a "Think of an {b}Objective{/b} like a point in a network."
    a "{b}Objective{/b}s can have predecessors, or ancestors."
    a "All of an {b}Objective{/b}'s predecessors must be completed before it becomes visible."
    a "{b}Objective{/b} can also have successors, or children."
    a "An {b}Objective{/b} is a predecessor of all its successors."
    a "Together this collection of {b}Objective{/b} forms a Quest."

label ask_alice:
    menu:
        "Tell me about {b}Objective{/b}s again.":
            a "Of course!"
            jump quest_types
        "Why are you saying {b}Objective{/b} funny? Why am I?":
            a "Any objects implemented as classes in this module are capitalized and marked with bold text."
            a "That includes: {b}Objective{/b}, {b}Quest{/b}, and their subclasses."
        "Tell me about the types of {b}Objective{/b}s in this module.":
            a "Basic {b}Objective{/b} only check if they are complete or not."
            a "Other {b}Objective{/b} are subclasses of {b}Objective{/b}."
            a "{b}CollectionObjective{/b} require you to get a certain number of something before they are complete."
            a "These can be used for fetch quests."
            a "You could also use them to drop a certain number of things, I guess."
            a "{b}BranchObjective{/b}s can end up in different states."
            a "These can be used to record choices."
            a "You can also make your own Objective, with the following syntax:"
            a "class MyObjective(Objective):"
            a "Feel free to examine the code for more details."
        "Tell me how {b}Quest{/b}s work.":
            a "A {b}Quest{/b} is just a collection of {b}Objective{/b}s with the knowledge of how they are related."
            a "Whenever you complete an {b}Objective{/b}, we mark that {b}Objective{/b} complete, then update the {b}Quest{/b}."
            a "The {b}Quest{/b} will tell us which {b}Objective{/b}s are now ready for you to complete next."
            a "When all the {b}Objective{/b}s have been completed, then the {b}Quest{/b} is complete too!"
            a "I can also tell you the implementation specifics, but they're a little more complex."
            $ knows_quest_basics = True
        "I know Python. Tell me how {b}Quest{/b}s are actually implemented." if knows_quest_basics:
            a "A {b}Quest{/b} is a directed acyclic graph of {b}Objective{/b}s implemented using Python's graphlib module."
            a "It stores the graph in a dict of the form {successor: {set, of, predecessors}}}."
            a "Calling prepare() sets up the {b}graphlib.TopologicalSorter{/b}, which is used to yield active objectives."
        "Tell me how the questlog works.":
            a "The questlog is implemented using RenPy Encyclopaedia 3.6.0 by jsfehler."
            a "But you could use another front end if you liked."
            a "The {b}Quest{/b} class exposes a method, summarize(), which returns all the {b}Objective{/b}s the player should be able to see."
            a "That includes completed and active {b}Objective{/b}s, but not hidden or future {b}Objective{/b}s."
            $ knows_hidden_objective = True
            a "From there, you can use the built-in str() function of {b}Objective{/b}s or something custom to make sure the player knows what they have to do."
            a "You don't even have to have a front end at all, if you want to keep things mysterious!"
        "Does this quest have a hidden objective?" if knows_hidden_objective:
            a "It does!"
            a "You'll need to give Eileen a password to complete the quest."
            call alice_password
        "Eileen said I should ask you for a password." if tutorial_quest.objective("get_password").hidden == False:
            a "Yes. This is an example of a hidden objective."
            call alice_password
        "I should go.":
            a "Please come back if you have additional questions!"
            jump main_quest
    jump ask_alice

label bob_main:
    if tutorial_quest.is_active("talk_bob"):
        b "Hey, you're Alice's friend, right?"
        b "I have the next step in your quest."
        b "I like beans."
        b "I really, REALLY like beans."
        b "Give me 10 beans, and I'll give you a prize."
        $ tutorial_quest.objective("talk_bob").mark_complete()
        $ tutorial_entry.update()
        #$ tutorial_quest.update()
    elif tutorial_quest.is_active("give_beans"):
        b "Hey again! Do you have my beans?"
        menu:
            "Not yet." if tutorial_quest.is_active("beans"):
                b "Then go get them!"
            "Yes, I do." if tutorial_quest.is_complete("beans"):
                b "Wow, great! Can I have them?"
                menu:
                    "Yes.":
                        b "Wow, thanks for the beans!"
                        b "Please talk to Eileen to complete the quest."
                        b "For your prize, here is a bar of chocolate."
                        b "I bought it because Carol and Dave both LOVE chocolate."
                        b "And I really like both of them."
                        b "But after I bought it I couldn't decide which one to give it to!"
                        b "So now it's your prize, but...."
                        b "Would you please give one of them the chocolate from me?"
                        $ tutorial_quest.objective("give_beans").mark_complete()
                        $ tutorial_entry.update()
                        #$ tutorial_quest.update()
                    "No.":
                        b "Then I guess you don't get the prize."
    elif tutorial_quest.objective("give_bar").status == "Carol":
        "Oh, Carol is here."
        "The two of them look busy. I should come back later."
    elif tutorial_quest.objective("give_bar").status == "Dave":
        "Oh, Dave is here."
        "The two of them look busy. I should come back later."
    else:
        b "Nice to see you again. I don't have any more chocolate though."
    return

label eileen_main:
    if not met_eileen:
        e "Hello. I'm Eileen. You'll turn in the quest to me when you're done."
        $ met_eileen = True
    if tutorial_quest.can_turn_in():
        e "Ready to get this over with?"
        menu:
            "Yes.":
                e "Great. I'll take that."
                $ tutorial_quest.turn_in()
                e "I'm supposed to tell you that the quest is complete in your log now."
                e "But unless you really want to check it again, I don't think that matters."
                jump done
            "No.":
                e "This isn't that interesting of a game, you know."
                e "Come back when you change your mind."
                jump main_quest
    elif tutorial_quest.is_complete("give_beans"):
        e "Good work at helping Bob."
        e "But there's one more thing you have to do. Tell me the password."
        jump eileen_password
    elif tutorial_quest.is_complete("get_password") and not tutorial_quest.is_complete("password"):
        e "There's a look in your eye."
        e "Is there something you want to tell me?"
        menu:
            "The password is catercorner.":
                e "Yes, it is."
                $ tutorial_quest.objective("password").mark_complete()
            "No.":
                "She shrugs."
                e "Suit yourself."
    else:
        e "I'm pretty sure you still have some stuff to do."
        e "Talk to me again if you think you're ready."

    if tutorial_quest.can_turn_in():
        jump eileen_main
    else:
        jump main_quest

label eileen_password:
    menu:
        "I didn't know there was a password!" if not knows_hidden_objective:
            e "Well, now you know."
            $ knows_hidden_objective = True
            e "Alice has it. Ask her."
            $ tutorial_quest.objective("get_password").hidden = False
            $ tutorial_quest.objective("password").hidden = False
        "Alice told me the password. It's catercorner." if tutorial_quest.is_complete("get_password"):
            e "That's exactly right!"
            $ tutorial_quest.objective("password").mark_complete()
            jump eileen_main
        "I'm ready to tell you the password." if knows_hidden_objective:
            e "Alright. What is it?"
            menu:
                "Quest.":
                    e "No."
                "Objective.":
                    e "Incorrect."
                "Beans.":
                    e "I'm not Bob!"
                "Kittycat":
                    e "No."
                "Catercorner.":
                    e "Yes!"
                    $ tutorial_quest.objective("password").mark_complete()
                "Cattywampus":
                    e "No."
                "Password.":
                    e "You're not even trying."
        "I'll come back later.":
            e "You do that."
            jump main_quest
    jump eileen_password

label alice_password:
    a "The password is: catercorner."
    $ tutorial_quest.objective("get_password").mark_complete()
    $ tutorial_quest.objective("password").hidden = False
    $ tutorial_entry.update()
    #$ tutorial_quest.update()
    return

label main_quest:
    menu:
        #"Show me my quest status.":
        #    a "[tutorial_quest]"
        "Talk to Alice again.":
            jump ask_alice
        "Talk to Bob.":
            call bob_main
        "Talk to Carol." if tutorial_quest.is_active("give_bar"):
            c "Hmm? Oh. Hello."
            c "Did you need something?"
            menu:
                "Just passing through.":
                    c "Alright."
                "I have a gift for you, from Bob.":
                    c "May I see?"
                    $ tutorial_quest.objective("give_bar").resolve("Carol")
                    $ tutorial_entry.update()
                    #$ tutorial_quest.update()
                    c "Oh, I do so adore chocolate. Thank you very much!"
                    c "I must go and give Bob my thanks as well."
                    c "Take care!"
        "Talk to Dave." if tutorial_quest.is_active("give_bar"):
            d "Hi!"
            d "What's up?"
            menu:
                "Just passing through.":
                    d "Don't be a stranger!"
                "I have a gift for you, from Bob.":
                    d "Sweet, I love gifts!"
                    $ tutorial_quest.objective("give_bar").resolve("Dave")
                    $ tutorial_entry.update()
                    #$ tutorial_quest.update()
                    d "Wow, this is great. Thanks!"
                    d "And it's from Bob? I gotta go tell him thanks too."
                    d "See ya!"
            $ tutorial_quest.objective("give_bar").resolve("Dave")
            $ tutorial_entry.update()
            #$ tutorial_quest.update()
        "Search for beans." if tutorial_quest.is_active("beans"):
            "You get on your knees and scrounge around for beans."
            python hide:
                n_beans = random.randint(1, 6)
                renpy.say(None, f"You feel a little silly, but you find {n_beans} beans.")
                tutorial_quest.objective("beans").collect(n_beans)
            # Will automatically mark itself complete when enough are collected.
        "Check your pockets.":
            "You shake out your pockets."
            if tutorial_quest.is_active("beans"):
                "You have [tutorial_quest.objective('beans').has] beans."
            elif tutorial_quest.is_active("give_bar"):
                "You have a chocolate bar. It's a little sticky."
                menu:
                    "Eat the bar.":
                        "You eat the entire chocolate bar. It's super delicious."
                        $ tutorial_quest.objective("give_bar").resolve("Eat it.")
                        $ tutorial_entry.update()
                        #$ tutorial_quest.update()
                    "Put it back.":
                        "You slip the chocolate bar back into your pocket."
            else:
                "You don't have anything in your pockets."
        "Talk to Eileen.":
            jump eileen_main
    if not tutorial_quest.completed:
        jump main_quest

label done:
    a "Congratulations. You've finished this quest tutorial!"
# This Ren'py files shows a method of displaying quest information
# Dependencies: renpy-encyclopaedia 3.x

init python:
    from quest import *
    import random
    
    toggle_log = False
    
    config.keymap['questlog'] = ['q']

    from encyclopaedia.encentry_ren import EncEntry

    # ---- Set up Encyclopaedia integration ----
    class QuestEntry(EncEntry):
        def __init__(self, quest, **kwargs):
            self._quest = quest
            self._state = None
            self._text = None # Per RenPy Encyclopaedia, _text must be list[str]
            self.bullet = "    •"

            super().__init__(name = quest.name, **kwargs)

        @property
        def text(self, show_all:bool = False):
            """
            Get the text for the quest entry. Update if the quest has changed.
            
            Overrides super.text
            
            :param show_all: Show hidden objectives in quest. Ex: for debug/dev mode.
            """
            if self.locked or self.locked is None:
                return self.locked_text
            if self._quest.state != self._state:
                self._update_text(show_all)
                self.viewed = False
            return self._text

        def update(self, show_all:bool = False) -> bool:
            """
            Update quest and let the Renpy game know.
            
            :param show_all: Show hidden objectives in quest. Ex: for debug/dev mode.
            """
            self._quest.update()
            if self._quest.state != self._state:
                self._update_text(show_all)
                self.viewed = False

        def _update_text(self, show_all:bool = False) -> bool:
            """
            Update the underlying text.
            
            :param show_all: Show hidden objectives in quest. Ex: for debug/dev mode.
            """
            self._state = self._quest.state
            objs = [self.bullet+str(obj) for obj in self._quest.summarize(show_all)]
            self._text = ["\n".join([self._quest.description] + objs)]
            if self._quest.completed:
                self.subject = "Completed Quests"
            elif self._quest.failed:
                self.subject = "Failed Quests"

"""
    def toggle_qlog():
        if renpy.get_screen(quest_log.list_screen):
            renpy.hide_screen(quest_log.list_screen)
        else:
            renpy.show_screen(quest_log.list_screen, quest_log, _layer="overlay")
            
    def ToggleCodex():
        global toggle_log
        if toggle_log:
            toggle_log = False
            renpy.exports.run(renpy.ui.returns(value))
        else:
            toggle_log = True
            ShowMenu(quest_log.list_screen, quest_log)()
"""

# Set up defaults so these are saved properly.
default quest_log = Encyclopaedia(name = "Quest Log")
default tutorial_quest = Quest(
    "My First Quest",
    "This quest is to show you how quests work."
)
default tutorial_entry = QuestEntry(tutorial_quest, parent=quest_log, locked=True)

# ---- Set up related hotkey screens ----

# This is also linked in the quick_menu
# textbutton _("Quest Log") action ShowMenu("questlog_wrapper")
screen questlog_wrapper():
    key "q" action Return()
    use encyclopaedia_list(quest_log) 

screen keymap_screen():
    layer "bottom"
    key "q" action ShowMenu("questlog_wrapper")
    key "o" action Show("objective_popup", message="keypress")

screen objective_popup(message):
    timer 2.0 action Hide("objective_popup", dissolve)

    frame:
        xalign 0.5
        yalign 0.0
        yoffset 20
        padding (20, 20)

        hbox:
            #spacing 10
            image "objective_complete.png"
            text message:
                yalign 0.5


init python:
    def notify_entry_updated(source):
        """This function is called when an entry is unlocked."""
        print(source)
        message = "Unlocked: Tutorial Quest"
        renpy.show_screen('objective_popup', message=message)

label callback:
    python:
        quest_log.subjects = ["Completed Quests", "Failed Quests"]
        
        quest_log.on("entry_unlocked")(notify_entry_updated)

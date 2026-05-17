import Quest
from encyclopaedia.encentry_ren import EncEntry

class QuestEntry(EncEntry):
    def __init__(self, quest, **kwargs):
        self._quest = quest
        self._state = None
        self._text = None # Per RenPy Encyclopaedia, _text must be list[str]
        super().__init__(name = quest.name, **kwargs)
    
    @property
    def text(self, bullet="    •", show_all = False):
        """
        Get the text for the quest entry. Update if the quest has changed.
        
        Overrides super.text
        """
        if self.locked or self.locked is None:
            return self.locked_text
        elif self._quest.state != self._state:
            # Quickly check if text needs updating: if yes, do heavy quest update.
            self._state = self._quest.state
            objs = [bullet+str(obj) for obj in self._quest.summarize(show_all)]
            self._text = ["\n".join([self._quest.description] + objs)]
            self.viewed = False
            if self._quest.completed:
                self.subject = "Completed Quests"
        return self._text
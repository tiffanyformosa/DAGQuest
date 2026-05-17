# DAGQuest

A Ren'Py library for managing quest logs using a DAG (Directed Acyclic Graph) architecture inspired by Python's [`graphlib`](https://docs.python.org/3/library/graphlib.html).

Instead of juggling booleans and flags to track quest state, DAGQuest lets you declare objectives and their dependencies — the library handles ordering, progression, and completion automatically.

---

## Features

- **Dependency-aware quest progression** — objectives unlock only when their prerequisites are met
- **Multiple objective types** — simple pass/fail, collection counters, and multi-ending branches
- **Optional objectives** — mark objectives as optional so they don't block quest completion
- **Hidden objectives** — hide objectives from the quest log until they become relevant
- **Journal integration** — `Journal.py` integrates with [Ren'Py Encyclopaedia](https://renpy-encyclopaedia.readthedocs.io/) for automatic quest log rendering
- **Efficient state tracking** — lightweight `state` property for change detection, avoiding unnecessary redraws

---

## Installation

Copy `Quest.py` (and optionally `Journal.py`) into your Ren'Py project's `game/` directory.

If you want to use `Journal.py`, you'll also need the [Ren'Py Encyclopaedia](https://renpy-encyclopaedia.readthedocs.io/) library installed.

---

## Core Concepts

### Objective

An `Objective` is a single step in a quest. Each objective has a **state**:

| State | Value | Meaning |
|---|---|---|
| `INPROGRESS` | `0` | Not yet done |
| `SUCCESS` | `1` | Completed |
| `FAIL` | `-1` | Failed — blocks successors |
| `DEAD` | `128` | Skipped — allows the graph to progress |

```python
obj = Objective("find_sword", "Find the legendary sword.")
obj.mark_complete()   # → SUCCESS
obj.mark_failed()     # → FAIL
obj.mark_dead()       # → DEAD (alias: obj.kill())
```

**Objective parameters:**

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Unique key used to reference this objective |
| `display_text` | `str` | Text shown in the quest log |
| `required` | `bool` | If `False`, won't block quest completion (default: `True`) |
| `hidden` | `bool` | If `True`, hidden from quest log until checked explicitly (default: `False`) |

---

### CollectionObjective

For fetch quests or counters. Mirrors Python's `range()` syntax.

```python
# Collect 5 herbs (counts up from 0)
herbs = CollectionObjective("collect_herbs", 5, display_text="Collect [stop] herbs.")

# Spend 10 gold (counts down from 10 to 0)
gold = CollectionObjective("spend_gold", 10, 0, display_text="Spend [stop] gold.")

herbs += 1        # collect one herb
herbs.collect(2)  # collect two more
```

In `display_text`, `[stop]` and `[start]` are automatically replaced with the initialized values.

---

### BranchObjective

For objectives with multiple possible endings (e.g. choices that diverge the story).

```python
endings = {
    "sided_with_guild": "You sided with the Thieves Guild.",
    "sided_with_guards": "You sided with the City Guard.",
}
choice = BranchObjective("faction_choice", endings, default_text="Choose a side.")

choice.resolve("sided_with_guild")
# or by index: choice.resolve(1)
```

---

### Quest

A `Quest` holds a graph of objectives and manages their topological ordering.

```python
quest = Quest("The Lost Relic", "Recover the ancient relic from the ruins.")

# Add objectives with dependencies
quest.add(find_entrance)              # no prerequisites
quest.add(defeat_guardian, find_entrance)
quest.add(retrieve_relic, defeat_guardian)
quest.add(return_home, retrieve_relic)

quest.prepare()   # locks in the graph and activates the first objectives
```

`quest.update()` must be called after objectives change state — it advances the graph and refreshes `quest.current` (the set of currently active objectives).

```python
find_entrance.mark_complete()
quest.update()
# defeat_guardian is now active
```

---

## Full Example

```python
from Quest import Objective, CollectionObjective, Quest

# Define objectives
talk_to_elder    = Objective("talk_elder",  "Speak to the village elder.")
gather_herbs     = CollectionObjective("gather_herbs", 5, display_text="Gather [stop] medicinal herbs.")
optional_chest   = Objective("open_chest", "Find the hidden chest.", required=False)
brew_potion      = Objective("brew_potion", "Brew the healing potion.")
deliver_potion   = Objective("deliver",    "Deliver the potion to the elder.")

# Build the quest graph
quest = Quest("The Healer's Errand", "Help the village elder cure the plague.")

quest.add(talk_to_elder)
quest.add(gather_herbs,   talk_to_elder)
quest.add(optional_chest, talk_to_elder)
quest.add(brew_potion,    gather_herbs)
quest.add(deliver_potion, brew_potion)

quest.prepare()
print(quest.current)
# → {talk_to_elder}

talk_to_elder.mark_complete()
quest.update()
# → {gather_herbs, optional_chest}

for _ in range(5):
    gather_herbs += 1
quest.update()
# → {optional_chest, brew_potion}

optional_chest.mark_dead()   # skip optional objective
brew_potion.mark_complete()
quest.update()
# → {deliver_potion}

deliver_potion.mark_complete()
quest.turn_in()
print(quest.completed)  # → True
```

---

## Quest Journal (Ren'Py Encyclopaedia)

`Journal.py` provides `QuestEntry`, a subclass of Ren'Py Encyclopaedia's `EncEntry`, for displaying quest state in a formatted quest log.

```python
from Journal import QuestEntry

entry = QuestEntry(quest, subject="Active Quests")
```

`QuestEntry.text` is lazily updated — it only recalculates when the quest's internal state has changed, making it safe to poll in Ren'Py's screen layer without performance issues. When a quest is completed, its subject automatically moves to `"Completed Quests"`.

---

## API Reference

### `Objective`

| Method / Property | Description |
|---|---|
| `mark_complete()` | Set state to SUCCESS |
| `mark_failed()` | Set state to FAIL |
| `mark_dead()` / `kill()` | Set state to DEAD |
| `done` | `True` if SUCCESS or DEAD |
| `success` | `True` if SUCCESS |
| `failed` | `True` if FAIL |
| `in_progress` | `True` if INPROGRESS |
| `status` | Human-readable state string |

### `CollectionObjective`

| Method / Property | Description |
|---|---|
| `collect(amount=None)` | Increment (or decrement) counter; auto-completes at target |
| `empty()` | Reset counter to start |
| `has` | Current count |

### `BranchObjective`

| Method / Property | Description |
|---|---|
| `resolve(state)` | Set ending by name (str) or index (int) |
| `valid_states` | List of declared ending names |
| `display_text` | Returns text corresponding to current state |

### `Quest`

| Method / Property | Description |
|---|---|
| `add(objective, *predecessors)` | Add an objective with optional prerequisites |
| `prepare()` | Finalize graph and activate initial objectives |
| `update()` | Advance graph after objectives change; refreshes `current` |
| `objective(name)` | Look up an objective by name |
| `is_active(name)` | Check if an objective is currently active |
| `is_complete(name)` | Check if an objective is done |
| `can_turn_in()` | Check if quest is ready to be completed |
| `turn_in()` | Mark quest as complete; returns `True` on success |
| `summarize(show_all=False)` | Generator yielding objectives in topological order |
| `current` | Set of currently active objectives |
| `completed` | `True` if quest status is COMPLETE |
| `state` | Bytes snapshot of quest state for efficient change detection |

---

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.

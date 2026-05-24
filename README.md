# DAGQuest

A Ren'Py library for managing quest logs using a DAG (Directed Acyclic Graph) architecture inspired by Python's [`graphlib`](https://docs.python.org/3/library/graphlib.html).

This backend handles objective dependencies, branching, and hidden objectives and can be paired with assorted front-ends for compatibility with Ren'py, Pygame and other engines.

---

## Features

- **Dependency-aware quest progression** — objectives unlock only when their prerequisites are met
- **Multiple objective types** — simple pass/fail, collection counters, and multi-ending branches
- **Optional objectives** — mark objectives as optional so they don't block quest completion
- **Hidden objectives** — hide objectives from the quest log until they become relevant

---

## Installation

Ren'py: Copy src/quest into your python-packages directory.

To play the example, you will also need to install jsfehler's [Ren'Py Encyclopaedia](https://renpy-encyclopaedia.readthedocs.io/).

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
# Collect 10 beans (counts up from 0)
beans = CollectionObjective("beans", 10, "Collect 10 beans.")

# Spend 10 gold (counts down from 10 to 0)
gold = CollectionObjective("spend_gold", 10, 0, display_text="Spend [stop] gold.")

beans.collect(3)  # collect three beans
```
In `display_text`, `[stop]` and `[start]` are automatically replaced with the initialized values.

---

### BranchObjective

For objectives with multiple possible endings (e.g. choices that diverge the story).

```python
endings = {
    "sided_with_thieves": "You sided with the Thieves Guild.",
    "sided_with_vampires": "You sided with the Vampire Clan.",
}
choice = BranchObjective("faction_choice", endings, default_text="Choose a side.")

choice.resolve("sided_with_thieves")
# or by index: choice.resolve(1)
```

---

### Quest

A `Quest` holds a graph of objectives and manages their topological ordering.

```python
quest = Quest("The Lost Relic", "Recover the treasure hoard from the ruins.")

# Add objectives with dependencies
quest.add(find_entrance)              # no prerequisites
quest.add(defeat_dragon, find_entrance)
quest.add(retrieve_treasure, find_entrance)
quest.add(return_home, retrieve_relic, defeat_dragon)

quest.prepare()   # locks in the graph and activates the first objectives
```

`quest.update()` must be called after objectives change state — it advances the graph and refreshes `quest.current` (the set of currently active objectives).

```python
find_entrance.mark_complete()
quest.update()
# defeat_dragon is now active
```

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
| `failed` | `True` if quest status is FAILED |
| `state` | Bytes snapshot of quest state for efficient change detection |

---

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.

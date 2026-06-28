# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Today's Schedule for Alex (90 min available)
---------------------------------------------
  08:00  Morning walk (30 min) [high] - Biscuit
  09:00  Feeding (10 min) [high] - Biscuit
  07:00  Litter box (15 min) [medium] - Mittens
  18:00  Grooming (20 min) [low] - Mittens

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

tests/test_pawpal.py ..                                                                                                          [100%]

========================================================== 
2 passed in 0.01s ===========================================================

## 📐 Smarter Scheduling

PawPal+ goes beyond a basic to-do list with the scheduling logic below. All of it
lives in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting by time | `Scheduler.sort_by_time()` | Orders all unfinished tasks chronologically (07:00 → 18:00), regardless of the order they were added. |
| Sorting by priority | `Scheduler.sort_tasks()` | Orders tasks high → low priority, then by soonest due time as a tiebreaker. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Narrows tasks by pet and/or completion status. Both filters are optional — pass neither to get everything. |
| Conflict detection | `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()`, `Task.overlaps()` | Flags any two tasks whose time windows overlap, for the same pet or different pets. Each `Conflict` knows via `.same_pet` whether it's one pet double-booked or two pets competing for the owner. `conflict_warnings()` returns plain warning strings instead of raising. |
| Recurring tasks | `Task.occurs_on(date)`, `Task.next_occurrence()`, `Scheduler.complete_task()`, `Scheduler.tasks_for_date(date)` | `occurs_on` decides whether a daily/weekly/once task lands on a given day; `next_occurrence` builds the next instance; `complete_task` marks a recurring task done and auto-schedules the next one. |

### How the pieces work

- **Sorting by time** — `sort_by_time()` uses `sorted()` with a `key` of each task's `due` datetime, so chronological order is correct no matter how tasks were entered.
- **Filtering** — `filter_tasks()` defaults both arguments to `None`, meaning "don't filter on this," so one method handles every combination (all tasks, one pet, by status, or both).
- **Conflict detection** — `Task.overlaps()` compares two time windows (`start < other.end and other.start < end`); `find_conflicts()` checks every task pair and returns `Conflict` objects, never crashing on a clash.
- **Recurring tasks** — `frequency` (`"daily"`, `"weekly"`, `"once"`) drives `occurs_on()` and `next_occurrence()`, which advances the due date by one day or one week using `timedelta`.

## 📸 Demo Walkthrough

Run the app with `streamlit run app.py`, then follow along:

1. **Set up the owner and pets.** Enter the owner's name, then add one or more pets (name + species). Your pets appear in a list.
2. **Add tasks.** Pick a pet, then add a task with a title, duration, priority, and due time (e.g. "Morning walk", 30 min, high, 08:00). Repeat for a few tasks across different pets and times.
3. **Filter the task list.** Use the **Pet** and **Status** dropdowns to narrow what's shown — e.g. just Biscuit's tasks, or only the pending ones. This calls `Scheduler.filter_tasks()`.
4. **Generate the daily plan.** Set the minutes available today and click **Generate schedule**. The app sorts tasks by priority and fits as many as the time allows, showing each task's time, duration, priority, and pet.
5. **See conflicts and recurring tasks.** These run in the logic layer (not yet wired into the Streamlit UI). Run `python main.py` to see the scheduler flag overlapping tasks (`find_conflicts()`) and auto-schedule the next occurrence when a daily/weekly task is completed (`complete_task()`).

The terminal demo (`python main.py`) exercises all of the above — sorting, filtering, conflicts, and recurring tasks — with sample data.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

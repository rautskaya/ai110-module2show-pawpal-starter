"""PawPal+ system classes.

Implements the four core objects from diagrams/uml_draft.mmd:
Task, Pet, Owner, and Scheduler. Data-holding objects use dataclasses
to stay clean; Scheduler holds the planning logic.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


# Lower number = higher priority, used for sorting.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

# How far ahead the next instance of a recurring task is due.
RECURRENCE_INTERVAL = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, etc.)."""

    description: str
    due: datetime  # when the task is due
    duration: int  # minutes
    priority: str  # "high", "medium", or "low"
    frequency: str = "daily"  # e.g. "daily", "weekly", "once"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a sortable number for this task's priority (high first)."""
        return PRIORITY_RANK.get(self.priority.lower(), len(PRIORITY_RANK))

    @property
    def end(self) -> datetime:
        """When the task finishes (start time + duration)."""
        return self.due + timedelta(minutes=self.duration)

    def overlaps(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another's."""
        return self.due < other.end and other.due < self.end

    def occurs_on(self, target: date) -> bool:
        """Return True if this task should appear on the given calendar date.

        Honors the recurrence in ``frequency``:
          * "once"   -> only on its original due date
          * "daily"  -> every day on or after the due date
          * "weekly" -> same weekday, on or after the due date
        """
        if target < self.due.date():
            return False
        freq = self.frequency.lower()
        if freq == "once":
            return target == self.due.date()
        if freq == "weekly":
            return target.weekday() == self.due.weekday()
        # Default to daily for "daily" or any unknown frequency.
        return True

    def next_occurrence(self) -> "Task | None":
        """Build the next instance of a recurring task, or None if it doesn't repeat.

        Daily tasks advance one day, weekly tasks one week. The new task keeps
        the same description, duration, priority, and frequency, and starts as
        not completed. "once" tasks (or unknown frequencies) return None.
        """
        interval = RECURRENCE_INTERVAL.get(self.frequency.lower())
        if interval is None:
            return None
        return Task(
            description=self.description,
            due=self.due + interval,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
        )


@dataclass
class Pet:
    """A pet that care tasks belong to."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def edit_task(self, description: str, **changes) -> bool:
        """Update fields on the task matching the description; return True if found."""
        for task in self.tasks:
            if task.description == description:
                for field_name, value in changes.items():
                    setattr(task, field_name, value)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks


@dataclass
class Owner:
    """The pet owner using the app."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all pets for this owner."""
        return self.pets

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task across all pets, paired with the pet it belongs to."""
        all_tasks: list[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks():
                all_tasks.append((pet, task))
        return all_tasks


@dataclass
class Conflict:
    """Two tasks whose scheduled time windows overlap."""

    pet_a: Pet
    task_a: Task
    pet_b: Pet
    task_b: Task

    @property
    def same_pet(self) -> bool:
        """True if both tasks belong to the same pet (impossible to do both at once)."""
        return self.pet_a is self.pet_b

    def describe(self) -> str:
        """Human-readable summary of the clash, tagged by severity."""
        scope = (
            f"{self.pet_a.name} can't do two things at once"
            if self.same_pet
            else f"{self.pet_a.name} and {self.pet_b.name} need you at the same time"
        )
        return (
            f"{self.task_a.description} ({self.pet_a.name}, "
            f"{self.task_a.due:%H:%M}-{self.task_a.end:%H:%M}) overlaps "
            f"{self.task_b.description} ({self.pet_b.name}, "
            f"{self.task_b.due:%H:%M}-{self.task_b.end:%H:%M}) — {scope}"
        )


class Scheduler:
    """Organizes tasks across all of an owner's pets into a daily plan."""

    def __init__(self, owner: Owner, available_time: int) -> None:
        """Create a scheduler for an owner with a daily time budget (minutes)."""
        self.owner = owner
        self.available_time = available_time  # minutes available in the day

    def collect_tasks(self) -> list[tuple[Pet, Task]]:
        """Return unfinished tasks across all pets, paired with their pet."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed
        ]

    def complete_task(self, pet: Pet, task: Task) -> "Task | None":
        """Mark a task done and auto-schedule its next occurrence if it recurs.

        Returns the newly created follow-up task (added to ``pet``), or None
        when the task does not repeat (e.g. a "once" task).
        """
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            pet.add_task(follow_up)
        return follow_up

    def sort_tasks(self) -> list[tuple[Pet, Task]]:
        """Order tasks by priority, then by soonest due time as a tiebreaker."""
        return sorted(
            self.collect_tasks(),
            key=lambda pair: (pair[1].priority_rank(), pair[1].due),
        )

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Order unfinished tasks chronologically — the owner's day as a timeline."""
        return sorted(self.collect_tasks(), key=lambda pair: pair[1].due)

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs narrowed by pet name and/or completion status.

        Both filters are optional; passing neither returns every task.
        """
        results: list[tuple[Pet, Task]] = []
        for pet, task in self.owner.get_all_tasks():
            if pet_name is not None and pet.name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            results.append((pet, task))
        return results

    def tasks_for_date(self, target: date) -> list[tuple[Pet, Task]]:
        """Return unfinished tasks that recur onto ``target``, sorted by time."""
        due = [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if not task.completed and task.occurs_on(target)
        ]
        return sorted(due, key=lambda pair: pair[1].due)

    def find_conflicts(self) -> list[Conflict]:
        """Return overlapping task pairs — whether for the same pet or different pets.

        Compares every unfinished task against every later one (sorted by time)
        and flags any whose time windows overlap. Each Conflict knows via
        ``same_pet`` whether the clash is one pet double-booked or two pets
        competing for the owner's attention.
        """
        ordered = self.sort_by_time()
        conflicts: list[Conflict] = []
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                (pet_a, task_a), (pet_b, task_b) = ordered[i], ordered[j]
                if task_a.overlaps(task_b):
                    conflicts.append(Conflict(pet_a, task_a, pet_b, task_b))
        return conflicts

    def conflict_warnings(self) -> list[str]:
        """Lightweight check: return human-readable conflict warnings, never raise.

        Returns one warning string per overlapping pair, or an empty list when
        the schedule is clean. Callers can print or display these directly —
        a scheduling clash is treated as something to warn about, not an error
        that crashes the program.
        """
        return [f"⚠️ Conflict: {c.describe()}" for c in self.find_conflicts()]

    def has_conflicts(self) -> bool:
        """True if any two scheduled tasks overlap in time."""
        return bool(self.find_conflicts())

    def generate_plan(self) -> list[tuple[Pet, Task]]:
        """Return the sorted tasks that fit within the available time, in order."""
        plan: list[tuple[Pet, Task]] = []
        time_left = self.available_time
        for pet, task in self.sort_tasks():
            if task.duration <= time_left:
                plan.append((pet, task))
                time_left -= task.duration
        return plan

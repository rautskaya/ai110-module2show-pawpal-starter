"""PawPal+ system classes.

Implements the four core objects from diagrams/uml_draft.mmd:
Task, Pet, Owner, and Scheduler. Data-holding objects use dataclasses
to stay clean; Scheduler holds the planning logic.
"""

from dataclasses import dataclass, field
from datetime import datetime


# Lower number = higher priority, used for sorting.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


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

    def sort_tasks(self) -> list[tuple[Pet, Task]]:
        """Order tasks by priority, then by soonest due time as a tiebreaker."""
        return sorted(
            self.collect_tasks(),
            key=lambda pair: (pair[1].priority_rank(), pair[1].due),
        )

    def generate_plan(self) -> list[tuple[Pet, Task]]:
        """Return the sorted tasks that fit within the available time, in order."""
        plan: list[tuple[Pet, Task]] = []
        time_left = self.available_time
        for pet, task in self.sort_tasks():
            if task.duration <= time_left:
                plan.append((pet, task))
                time_left -= task.duration
        return plan

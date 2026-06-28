"""PawPal+ system classes.

Class stubs based on the UML in diagrams/uml_draft.mmd.
Data-holding objects (Task, Pet) use dataclasses to stay clean.
No logic yet — methods are stubs to be filled in later.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, etc.)."""

    name: str
    duration: int  # minutes
    priority: str  # "high", "medium", or "low"

    def summary(self) -> str:
        """Return a short, readable description of the task."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet that care tasks belong to."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        raise NotImplementedError

    def edit_task(self, task: Task) -> None:
        """Update an existing task on this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner using the app."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        """Return all pets for this owner."""
        raise NotImplementedError


@dataclass
class Plan:
    """The finished daily schedule produced by the Scheduler."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_time: int = 0

    def display(self) -> str:
        """Return the plan as readable text."""
        raise NotImplementedError


class Scheduler:
    """Turns a list of tasks into a daily plan based on constraints."""

    def __init__(self, tasks: list[Task], available_time: int) -> None:
        self.tasks = tasks
        self.available_time = available_time  # minutes available in the day

    def sort_tasks(self) -> list[Task]:
        """Return tasks ordered by priority (and duration as a tiebreaker)."""
        raise NotImplementedError

    def generate_plan(self) -> Plan:
        """Fit tasks into the available time and return a Plan."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Explain why the scheduler chose this plan."""
        raise NotImplementedError

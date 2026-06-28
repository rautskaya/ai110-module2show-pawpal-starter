"""Tests for PawPal+ core logic."""

from datetime import datetime

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def scheduler():
    """An owner with two pets and a mix of completed/pending tasks."""
    owner = Owner("Alex")
    biscuit, mittens = Pet("Biscuit", "dog"), Pet("Mittens", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    biscuit.add_task(Task("Morning walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    done = Task("Feeding", datetime(2026, 6, 28, 9, 0), 10, "high")
    done.mark_complete()
    biscuit.add_task(done)
    mittens.add_task(Task("Litter box", datetime(2026, 6, 28, 7, 0), 15, "medium"))

    return Scheduler(owner, 90)


def test_mark_complete_changes_status():
    # A new task starts as not completed.
    task = Task("Morning walk", datetime(2026, 6, 28, 8, 0), 30, "high")
    assert task.completed is False

    # After mark_complete(), it should be marked done.
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", datetime(2026, 6, 28, 9, 0), 10, "high"))
    assert len(pet.get_tasks()) == 1


def _descriptions(pairs):
    """Pull just the task descriptions out of (pet, task) pairs."""
    return {task.description for _, task in pairs}


def test_filter_no_args_returns_every_task(scheduler):
    assert _descriptions(scheduler.filter_tasks()) == {
        "Morning walk",
        "Feeding",
        "Litter box",
    }


def test_filter_by_pet_name(scheduler):
    result = scheduler.filter_tasks(pet_name="Biscuit")
    assert _descriptions(result) == {"Morning walk", "Feeding"}


def test_filter_by_completed_true(scheduler):
    result = scheduler.filter_tasks(completed=True)
    assert _descriptions(result) == {"Feeding"}


def test_filter_by_completed_false_excludes_done(scheduler):
    result = scheduler.filter_tasks(completed=False)
    assert _descriptions(result) == {"Morning walk", "Litter box"}


def test_filter_by_pet_and_status_combined(scheduler):
    result = scheduler.filter_tasks(pet_name="Biscuit", completed=False)
    assert _descriptions(result) == {"Morning walk"}


def test_sort_by_time_returns_chronological_order():
    # Tasks added out of order should come back earliest-first.
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Evening walk", datetime(2026, 6, 28, 18, 0), 30, "low"))
    pet.add_task(Task("Morning walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    pet.add_task(Task("Lunch feed", datetime(2026, 6, 28, 12, 0), 10, "medium"))

    ordered = Scheduler(owner, 120).sort_by_time()
    assert [task.description for _, task in ordered] == [
        "Morning walk",
        "Lunch feed",
        "Evening walk",
    ]


def test_sort_tasks_orders_by_priority_then_due_time():
    # Priority wins; due time breaks ties within the same priority.
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Late high", datetime(2026, 6, 28, 10, 0), 30, "high"))
    pet.add_task(Task("Early high", datetime(2026, 6, 28, 8, 0), 30, "high"))
    pet.add_task(Task("Early low", datetime(2026, 6, 28, 7, 0), 30, "low"))

    ordered = Scheduler(owner, 120).sort_tasks()
    assert [task.description for _, task in ordered] == [
        "Early high",
        "Late high",
        "Early low",
    ]


def test_detects_conflict_for_identical_times():
    # Two tasks scheduled at the exact same start time must be flagged.
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    pet.add_task(Task("Meds", datetime(2026, 6, 28, 8, 0), 10, "high"))

    conflicts = Scheduler(owner, 90).find_conflicts()
    assert len(conflicts) == 1


def test_daily_task_next_occurrence_advances_one_day():
    task = Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high", frequency="daily")
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.due == datetime(2026, 6, 29, 8, 0)
    assert nxt.completed is False


def test_weekly_task_next_occurrence_advances_one_week():
    task = Task("Bath", datetime(2026, 6, 28, 11, 0), 45, "medium", frequency="weekly")
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.due == datetime(2026, 7, 5, 11, 0)


def test_once_task_has_no_next_occurrence():
    task = Task("Vet visit", datetime(2026, 6, 28, 8, 0), 30, "high", frequency="once")
    assert task.next_occurrence() is None


def test_complete_task_reschedules_recurring(scheduler):
    pet = scheduler.owner.get_pets()[0]  # Biscuit
    walk = next(t for t in pet.get_tasks() if t.description == "Morning walk")

    follow_up = scheduler.complete_task(pet, walk)

    # Original is done; a fresh instance exists for the next day.
    assert walk.completed is True
    assert follow_up is not None
    assert follow_up.due == datetime(2026, 6, 29, 8, 0)
    assert follow_up in pet.get_tasks()


def test_complete_task_does_not_reschedule_once():
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    visit = Task("Vet visit", datetime(2026, 6, 28, 8, 0), 30, "high", frequency="once")
    pet.add_task(visit)

    follow_up = Scheduler(owner, 60).complete_task(pet, visit)

    assert visit.completed is True
    assert follow_up is None
    assert len(pet.get_tasks()) == 1


def test_no_conflicts_when_tasks_dont_overlap():
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    pet.add_task(Task("Feed", datetime(2026, 6, 28, 9, 0), 10, "high"))

    assert Scheduler(owner, 90).find_conflicts() == []


def test_detects_same_pet_conflict():
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    pet.add_task(Task("Meds", datetime(2026, 6, 28, 8, 10), 10, "high"))

    conflicts = Scheduler(owner, 90).find_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0].same_pet is True


def test_detects_different_pet_conflict():
    owner = Owner("Sam")
    rex, milo = Pet("Rex", "dog"), Pet("Milo", "cat")
    owner.add_pet(rex)
    owner.add_pet(milo)
    rex.add_task(Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    milo.add_task(Task("Vet", datetime(2026, 6, 28, 8, 15), 30, "high"))

    conflicts = Scheduler(owner, 90).find_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0].same_pet is False


def test_conflict_warnings_empty_when_clean():
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high"))

    scheduler = Scheduler(owner, 90)
    assert scheduler.conflict_warnings() == []
    assert scheduler.has_conflicts() is False


def test_conflict_warnings_returns_strings_without_raising():
    owner = Owner("Sam")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    pet.add_task(Task("Meds", datetime(2026, 6, 28, 8, 10), 10, "high"))

    scheduler = Scheduler(owner, 90)
    warnings = scheduler.conflict_warnings()  # must not raise
    assert len(warnings) == 1
    assert isinstance(warnings[0], str)
    assert "Conflict" in warnings[0]
    assert scheduler.has_conflicts() is True

"""Tests for PawPal+ core logic."""

from datetime import datetime

from pawpal_system import Pet, Task


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

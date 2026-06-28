"""Temporary testing ground for PawPal+ logic.

Run with: python main.py
Builds a sample owner, pets, and tasks, then prints today's schedule.
"""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # 1. Create an owner.
    owner = Owner("Alex")

    # 2. Create at least two pets and add them to the owner.
    biscuit = Pet("Biscuit", "dog")
    mittens = Pet("Mittens", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # 3. Add at least three tasks with different times.
    biscuit.add_task(Task("Morning walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    biscuit.add_task(Task("Feeding", datetime(2026, 6, 28, 9, 0), 10, "high"))
    mittens.add_task(Task("Litter box", datetime(2026, 6, 28, 7, 0), 15, "medium"))
    mittens.add_task(Task("Grooming", datetime(2026, 6, 28, 18, 0), 20, "low"))

    # 4. Build a plan and print today's schedule.
    available_time = 90  # minutes available today
    scheduler = Scheduler(owner, available_time)
    plan = scheduler.generate_plan()

    print(f"Today's Schedule for {owner.name} ({available_time} min available)")
    print("-" * 45)
    for pet, task in plan:
        print(
            f"  {task.due:%H:%M}  {task.description} "
            f"({task.duration} min) [{task.priority}] - {pet.name}"
        )


if __name__ == "__main__":
    main()

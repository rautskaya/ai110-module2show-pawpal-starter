"""Temporary testing ground for PawPal+ logic.

Run with: python main.py
Builds a sample owner, pets, and tasks, then prints today's schedule.
"""

from datetime import date, datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # 1. Create an owner.
    owner = Owner("Alex")

    # 2. Create at least two pets and add them to the owner.
    biscuit = Pet("Biscuit", "dog")
    mittens = Pet("Mittens", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # 3. Add tasks deliberately OUT OF TIME ORDER (18:00 before 07:00, etc.)
    #    so sort_by_time() has real work to do.
    mittens.add_task(Task("Grooming", datetime(2026, 6, 28, 18, 0), 20, "low"))
    biscuit.add_task(Task("Feeding", datetime(2026, 6, 28, 9, 0), 10, "high"))
    mittens.add_task(Task("Litter box", datetime(2026, 6, 28, 7, 0), 15, "medium"))
    biscuit.add_task(Task("Morning walk", datetime(2026, 6, 28, 8, 0), 30, "high"))
    # A weekly bath (Sundays) and a vet visit that overlaps the morning walk.
    biscuit.add_task(
        Task("Weekly bath", datetime(2026, 6, 28, 11, 0), 45, "medium", frequency="weekly")
    )
    mittens.add_task(
        Task("Vet visit", datetime(2026, 6, 28, 8, 15), 30, "high", frequency="once")
    )
    # Overlaps Biscuit's own 08:00 walk -> a same-pet (impossible) conflict.
    biscuit.add_task(Task("Medication", datetime(2026, 6, 28, 8, 10), 10, "high"))

    # Mark one task done so the status filter has something to separate.
    biscuit.edit_task("Feeding", completed=True)

    # Show the raw insertion order to contrast against the sorted views below.
    print("Tasks as added (insertion order):")
    for pet, task in owner.get_all_tasks():
        print(f"  {task.due:%H:%M}  {task.description} ({pet.name})")
    print()

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

    # 5. Chronological timeline view (sort by time).
    print("\nFull day, in time order:")
    print("-" * 45)
    for pet, task in scheduler.sort_by_time():
        print(f"  {task.due:%H:%M}-{task.end:%H:%M}  {task.description} ({pet.name})")

    # 6. Filter by pet, then by status.
    print("\nBiscuit's tasks only (filter by pet):")
    for _, task in scheduler.filter_tasks(pet_name="Biscuit"):
        done = "done" if task.completed else "pending"
        print(f"  - {task.description} ({done})")

    print("\nPending tasks only (filter by status):")
    for pet, task in scheduler.filter_tasks(completed=False):
        print(f"  - {task.description} ({pet.name})")

    print("\nCompleted tasks only (filter by status):")
    for pet, task in scheduler.filter_tasks(completed=True):
        print(f"  - {task.description} ({pet.name})")

    # 7. Recurring tasks: what actually lands on a given date.
    target = date(2026, 7, 5)  # the following Sunday
    print(f"\nTasks recurring onto {target:%A %Y-%m-%d}:")
    for _, task in scheduler.tasks_for_date(target):
        print(f"  - {task.description} [{task.frequency}]")

    # 8. Conflict detection: flag overlapping time windows (same or different pet).
    conflicts = scheduler.find_conflicts()
    print("\nScheduling conflicts:")
    if not conflicts:
        print("  None — your day is clear of overlaps.")
    for conflict in conflicts:
        flag = "⛔" if conflict.same_pet else "⚠️"
        print(f"  {flag}  {conflict.describe()}")


if __name__ == "__main__":
    main()

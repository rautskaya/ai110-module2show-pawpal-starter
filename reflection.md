# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

A user of PawPal+ should be able to:

1. **Add a pet** — type in the owner's name and the pet's name so the app knows who the plan is for.
2. **Add tasks** — add things like walks, feeding, or meds, and say how long each takes and how important it is.
3. **See the daily plan** — get a list of what to do that day, in order, based on the time you have and what matters most.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My first design had four main objects:

- **Owner** — holds the owner's name and their list of pets. It can add a pet and list its pets.
- **Pet** — holds the pet's name, type, and its list of tasks. It can add, edit, and list tasks.
- **Task** — holds one care task with its name, how long it takes, and how important it is. It can show itself as text.
- **Scheduler** — holds the list of tasks and the time available in the day. It sorts the tasks by priority, builds the daily plan, and explains why it chose that plan.

They connect like this: an Owner has one or more Pets, each Pet has many Tasks, and the Scheduler takes those Tasks plus the available time to make the daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design changed a few times as I reviewed it:

- **Task became a real to-do item.** At first it only had a name, duration, and priority. I changed it to hold a `description`, a `due` time, and a `completed` status, and added a `mark_complete()` method so a task can actually be checked off.
- **Scheduler now works across all pets.** Originally it took just one list of tasks. I changed it to take the `Owner` and added `collect_tasks()` so it pulls tasks from every pet, not just one.
- **Removed the Plan class.** I first had a separate `Plan` object, but it added complexity I didn't need, so I had `generate_plan()` simply return the scheduled tasks instead.
- **Linked tasks to pets and used the due time.** I made the scheduler return `(pet, task)` pairs so the plan can show which pet each task is for, skip tasks already done, and sort by priority and then soonest due time.

I made these changes after AI reviewed the skeleton and it showed missing pieces (like completion status) and a Scheduler that couldn't really handle more than one pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler looks at four things:

- **Priority** — each task is high, medium, or low. High-priority tasks come first.
- **Time available** — the owner says how many minutes they have that day, and the plan only adds tasks that fit in that time.
- **Due time** — when two tasks have the same priority, the one due earlier goes first.
- **Done or not** — finished tasks are skipped so the plan only shows what's left.

I decided priority mattered most because some tasks (like feeding or meds) can't be skipped, while others (like grooming) can wait. So the scheduler sorts by priority first, then uses the due time to break ties, and finally drops any task that doesn't fit in the time the owner has.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler is "greedy": it adds tasks in priority order and stops when the time runs out. This doesn't always fit the most tasks — skipping one long task could have made room for two short ones, but it won't rearrange to find that.

That's fine here because a pet owner cares more about getting the important tasks done (like feeding or meds) than about fitting the largest number of small ones. A simple, predictable plan is easier to trust.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

Sorting (chronological order, and priority with due time as a tiebreaker), filtering (by pet, by status, both combined, and no-args), conflict detection (same-pet, different-pet, and identical start times), and recurring tasks (completing a daily task creates a new one for the next day, weekly advances a week, and "once" creates nothing).

- Why were these tests important?

These are the behaviors a pet owner actually depends on — the plan has to be in the right order, show the right tasks, warn about clashes, and keep recurring care on schedule. A bug in any of them would quietly break the daily plan, so locking them down with tests guards against future changes breaking them.

**b. Confidence**

- How confident are you that your scheduler works correctly?

Fairly confident — about 4 out of 5. All 20 tests pass, and the parts pet owners rely on most (sorting, filtering, conflict detection, and recurring tasks) are directly verified. I'm holding back the last point because `generate_plan()`, the app's headline feature, isn't tested yet.

- What edge cases would you test next if you had more time?

`generate_plan()` respecting the time budget (and skipping a too-big task while still fitting a smaller later one), the `occurs_on()` / `tasks_for_date()` calendar logic, the weekly year rollover (Dec → Jan), and the back-to-back boundary where one task ends exactly as the next begins.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

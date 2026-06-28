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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

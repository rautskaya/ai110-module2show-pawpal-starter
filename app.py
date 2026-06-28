from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pets")
owner_name = st.text_input("Owner name", value="Jordan")

# Streamlit reruns this whole script on every click, so create the Owner
# only once and keep it in session_state so its pets/tasks persist.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)

owner = st.session_state.owner
# Keep the stored owner's name in sync with the text box.
owner.name = owner_name

# --- Add a pet (handled by Owner.add_pet) ---
col_a, col_b = st.columns(2)
with col_a:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_b:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))
    st.success(f"Added {pet_name} the {species}!")

pets = owner.get_pets()
if pets:
    st.write("**Your pets:** " + ", ".join(f"{p.name} ({p.species})" for p in pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.markdown("### Tasks")

if pets:
    # --- Add a task to a chosen pet (handled by Pet.add_task) ---
    selected_pet_name = st.selectbox("Add task to which pet?", [p.name for p in pets])
    selected_pet = next(p for p in pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    due_time = st.time_input("Due time", value=time(8, 0))

    if st.button("Add task"):
        due = datetime.combine(date.today(), due_time)
        selected_pet.add_task(Task(task_title, due, int(duration), priority))
        st.success(f"Added '{task_title}' for {selected_pet.name}.")

    # --- Filter the task list by pet and/or status ---
    st.markdown("**Show tasks**")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in pets])
    with fcol2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Done"])

    # Translate the dropdown choices into filter_tasks() arguments.
    pet_name = None if pet_filter == "All pets" else pet_filter
    completed = {"All": None, "Pending": False, "Done": True}[status_filter]

    # filter_tasks() ignores the time budget, so any value works here.
    filtered = Scheduler(owner, 0).filter_tasks(pet_name=pet_name, completed=completed)

    if filtered:
        for pet, t in filtered:
            done = "✅" if t.completed else "⬜"
            st.write(
                f"- {done} {t.due:%H:%M} {t.description} "
                f"({t.duration} min) [{t.priority}] — {pet.name}"
            )
    else:
        st.caption("No tasks match this filter.")
else:
    st.info("Add a pet before adding tasks.")

st.divider()

st.subheader("Build Schedule")

available_time = st.number_input(
    "Time available today (minutes)", min_value=1, max_value=1440, value=90
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner, int(available_time))
    plan = scheduler.generate_plan()

    if plan:
        st.write(f"**Today's Schedule for {owner.name}:**")
        for pet, task in plan:
            st.write(
                f"- {task.due:%H:%M} — {task.description} "
                f"({task.duration} min) [{task.priority}] for {pet.name}"
            )
    else:
        st.info("No tasks fit in the available time. Add tasks or increase the time.")

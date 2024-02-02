import streamlit as st
from pydantic import BaseModel
import sqlite3
from datetime import date

# Define Pydantic model for Task
class TaskModel(BaseModel):
    name: str
    description: str
    is_done: bool
    due_date: date  # Change the type to datetime.date
    category: str

# Create SQLite database and table
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS tasks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              description TEXT,
              is_done BOOLEAN NOT NULL,
              due_date TEXT,
              category TEXT
          )
          ''')

conn.commit()

# Streamlit app
def main():
    st.title("Zaayush's Tasker")  # Renamed the app

    # Create Task form
    task = TaskModel(
        name=st.text_input('Task Name'),
        description=st.text_area('Task Description'),
        is_done=st.checkbox('Is Done'),
        due_date=st.date_input('Due Date'),  # Added calendar style date selection
        category=st.selectbox(
            'Category',
            ['Work', 'Personal', 'Study'],  # Dropdown for category selection
        )
    )

    # Color dictionary for categories
    category_color = {
        'Work': 'red',
        'Personal': 'blue',
        'Study': 'green'
    }

    # Submit Task button
    if st.button('Submit Task'):
        # Insert new task into the database
        c.execute('INSERT INTO tasks (name, description, is_done, due_date, category) VALUES (?, ?, ?, ?, ?)',
                  (task.name, task.description, task.is_done, task.due_date, task.category))
        conn.commit()

    # Display tasks
    tasks = c.execute('SELECT * FROM tasks').fetchall()
    st.header('Task List')

    for task in tasks:
        task_id, name, description, is_done, due_date, category = task
        task_status = 'Done' if is_done else 'Not Done'
        task_color = category_color.get(category, 'black')
        task_checkbox = st.checkbox(
            f'{name} - {task_status}',
            value=is_done,
            key=f'checkbox_{task_id}',
            help=f'Due Date: {due_date}',
        )

        # Delete button
        delete_button = st.button(f'Delete {name}', key=f'delete_{task_id}')

        # Update task status on checkbox toggle
        if task_checkbox:
            c.execute('UPDATE tasks SET is_done = ? WHERE id = ?', (True, task_id))
        else:
            c.execute('UPDATE tasks SET is_done = ? WHERE id = ?', (False, task_id))

        # Delete task on button click
        if delete_button:
            c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()

    # Close database connection
    conn.close()

if __name__ == '__main__':
    main()

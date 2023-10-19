*****README*****
Task Manager Application

Introduction:
    This is a task management application built using Python, SQLite, Flask, HTML, and CSS. 
    It allows users to create, view, edit, delete, sort, and search tasks with various options.

The application provides two main functionalities:
    User Authentication:
        Allows users to register, login, and logout.
    Task Management:
        Users can create new tasks, view a list of their tasks, update task details, and delete tasks.
        Each task can have a status ("completed","not completed","overdiew), and users should be able to change the status of the tasks.
        Users can sort their tasks based on different criteria (e.g., by status,duedate).
        The application provides a search feature that lets users search for specific tasks by title,duedate etc.

Dependencies:
The following dependencies are required to run the application:
    antiorm==1.2.1
    blinker==1.6.3
    click==8.1.7
    colorama==0.4.6
    db==0.1.1
    db-sqlite3==0.0.1
    Flask==3.0.0
    itsdangerous==2.1.2
    Jinja2==3.1.2
    MarkupSafe==2.1.3
    Werkzeug==3.0.0

Installation Steps:
    Clone the repository from GitHub using git clone https://github.com/vishnupriyamurugavel/Task-Master.git
    Create a virtual environment with python -m venv env
    Activate the virtual environment with source env/Scripts/activate
    Install the dependencies with pip install -r requirements.txt
    create config.py file with SECRET_KEY = "secretkey"
    Run the application with flask run
    Open a web browser and navigate to http://localhost:5000/

Usage
User Authentication:
    Register a new account by clicking on the "Register" button .
    Fill out the registration form fields and submit.
    Login using your username and password by clicking the "Login" .
Task Management
    Create a new task list by clicking on the "New list" button in the lists page.
    Create a new task by clicking on the "New Task" button in the tasks page.
    Fill out the information on the task creation form and submit.
    View all your tasks in table format on the homepage.
    Edit a task by clicking on the "Edit" button on the task row.
    Change the status of a task by clicking on the "Done" or "Undo" option.
    Delete a task by clicking on the "Delete" button on the task row.
    Sort your tasks by clicking on any of the header columns.
    Search for a task using the "Search" bar at the top of the page by entering a title or description keyword.

Conclusion
    This application provides users with a convenient way to manage their tasks. 
    The documentation provides clear and concise instructions on how to install and use the application.

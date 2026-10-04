# College Department Management System

## Project Overview

The College Department Management System is a web-based application developed to manage college departments and their related academic information.

The system provides a simple interface for managing:

- Departments
- Faculty
- Students
- Courses

## Technologies Used

- HTML
- CSS
- JavaScript
- Python
- Flask
- MySQL
- mysql-connector-python
- Gunicorn

## Main Features

### Department Management
- Add department records
- View department records
- Edit department records
- Delete department records
- Search department records

### Faculty Management
- Add faculty records
- View faculty records
- Edit faculty records
- Delete faculty records
- Search faculty records

### Student Management
- Add student records
- View student records
- Edit student records
- Delete student records
- Search student records

### Course Management
- Add course records
- View course records
- Edit course records
- Delete course records
- Search course records

## Database

The application uses MySQL as the database management system.

The database contains tables for:

- Departments
- Faculty
- Students
- Courses

The `schema.sql` file contains the SQL database structure used for the project.

## Project Structure

```text
CollegeDepartmentManagementSystem/
│
├── app.py
├── schema.sql
├── requirements.txt
├── .gitignore
├── README.md
│
├── static/
│   └── ...
│
└── templates/
    └── ...
```

## Running the Project Locally

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Make sure MySQL is running and the required database is configured.

Then run:

```bash
python app.py
```

Open the local Flask application in a web browser.

## Project Status

The project is developed and tested as a local Flask and MySQL web application. The source code is maintained on GitHub.

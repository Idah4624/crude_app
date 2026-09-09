# Student Management System

A professional CRUD (Create, Read, Update, Delete) web application built with Flask, SQLite, Bootstrap, HTML, CSS, and JavaScript.

## Features

### Authentication

* User Login
* User Logout
* Session Management

### Student Management

* Add Students
* View Students
* Edit Student Records
* Delete Student Records
* Student Details Page

### Search & Filtering

* Search by Name
* Search by Email
* Search by Phone Number
* Filter by Course

### Dashboard

* Total Students
* Total Courses
* Male Students Count
* Female Students Count


### User Experience

* Responsive Design
* Flash Messages
* Delete Confirmation Dialog
* Pagination

## Technologies Used

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

## Project Structure

```text
crud_app/
│
├── app.py
├── database.db
├── requirements.txt
├── README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   ├── details.html
│   └── 404.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/student-management-system.git
cd student-management-system
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

### Activate Virtual Environment

Linux/Mac:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Default Login

```text
Username: admin
Password: admin123
```

## Future Improvements

* Password Hashing
* Role-Based Access Control
* Export to CSV
* Export to Excel
* Export to PDF
* REST API
* PostgreSQL Integration
* Activity Logs
* Student Photo Upload
* Email Notifications

## Author

Idah Onuh John

Software Engineer | Full-Stack Python Developer | Generative AI Enthusiast

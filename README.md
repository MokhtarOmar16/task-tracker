# Project Documentation: TaskFlow

## 1. Project Overview
TaskFlow is a social productivity web application designed to help users manage daily tasks while leveraging social accountability through streaks and public visibility. Built with **Django (SSR)**, it focuses on the "when" of productivity, allowing users to track their progress over time and compete with friends.

---

## 2. Core Features

### 👤 User Authentication
- **Secure Signup/Login:** Built using Django's `contrib.auth` system.
- **User Profiles:** Displays the user's current streak, total tasks completed, and friend list.

### ✅ Task Management
- **Task CRUD:** Create, Read, and Delete tasks.
- **Privacy Controls:** - **Public:** Tasks visible to friends on your social feed.
  - **Private:** Tasks visible only to the creator.
- **Rich Notes:** Add context, sub-steps, or progress updates to any task.

### 📈 Tracking & Streaks
- **Historical Tracker:** A dedicated view to filter tasks by date and visualize completion history.
- **Dynamic Streaks:**
  - A streak increments for every consecutive day at least one task is completed.
  - **Social Streaks:** Streaks are always public to foster friendly competition among friends.

### 🤝 Social Integration
- **Friend System:** Add/Follow other users to build a network.
- **Social Feed:** See what your friends are working on (Public tasks only) and monitor their streak status.

---

## 3. Technical Stack
- **Framework:** Django 5.x (Server-Side Rendering)
- **Frontend:** Django Templates + Tailwind CSS / Bootstrap
- **Database:** PostgreSQL (Production) / SQLite (Development)

---

## 4. Proposed Database Schema

| Model | Fields | Description |
| :--- | :--- | :--- |
| **User** | `username`, `email`, `current_streak`, `longest_streak` | Custom User model extending AbstractUser. |
| **Task** | `user`, `title`, `notes`, `is_public`, `created_at` | Core task data and privacy toggle. |
| **TaskCompletion** | `task`, `completed_at` | Log entry for when a task is finished. |
| **Friendship** | `from_user`, `to_user`, `created_at` | Many-to-many relationship for social features. |

---

## 5. Development Roadmap

### Phase 1: Authentication & Layout
- Initialize Django project.
- Setup CSS framework for a modern design.
- Implement Login/Signup/Logout views and templates.

### Phase 2: Task Engine
- Build the `Task` model and basic CRUD views.
- Implement the "Notes" field and "Privacy" toggle.
- Create the dashboard view listing today's tasks.

### Phase 3: The Tracker & Logic
- Build a "History" view that shows tasks finished on specific dates.
- Write the logic to calculate and update streaks based on daily completions.

### Phase 4: Social Features
- Implement friend requests/following logic.
- Create the "Social Feed" where public tasks and streaks are displayed.
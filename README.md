
# 🧑‍💻 LinkedIn Automation Tool

A Django web app that automates searching for professionals on LinkedIn and sending connection requests — all while keeping user control and ethical use at the forefront.

> ⚠️ This tool does **not bypass LinkedIn’s security features** like OTP or CAPTCHA.  
> It opens a visible browser so users can complete verification steps manually when needed.

---

## 🔍 Features

- ✅ Log into LinkedIn via the app
- 📊 Search for people by domain/interest (e.g., AI, Marketing)
- 🤖 Automatically extract public profile links from search results
- 💬 Send personalized invites with optional message template
- ⏱ Randomized delays between actions to avoid detection
- 🔐 No passwords stored in DB — uses session-based handling only
- 📋 Debugging tools: logs, screenshots, and HTML saving for troubleshooting

---

## 🧩 Technologies Used

| Tech | Purpose |
|------|---------|
| **Django** | Web framework for authentication and views |
| **Playwright** | Browser automation for login, search, and invite sending |
| **HTML + Bootstrap** | Clean and responsive templates |
| **Session Storage** | Safe passing of credentials between views |
| **CSRF Protection** | Secure form handling |

---

## 🧪 How It Works

1. User enters LinkedIn credentials and a domain (e.g., "AI")
2. App opens Chromium and logs into LinkedIn
3. Performs search and extracts public profile URLs
4. User confirms before sending invites
5. Invites are sent one-by-one with random delay

---

## 📦 Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/linkedin-automation.git
cd linkedin-automation
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # On Mac/Linux
.\.venv\Scripts\activate    # On Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start development server
```bash
python manage.py runserver
```

Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧪 Usage

1. **Register or Log In** to the Django app.
2. Enter your **LinkedIn email/password + domain** (e.g., AI, Marketing).
3. Click **"Search"** – Chromium browser opens and logs you into LinkedIn.
4. Wait up to **10 seconds** if OTP screen appears → complete it manually.
5. View extracted profiles → click **"Send Invites"**
6. Watch as the script sends invites one-by-one using Playwright.

---

## 📁 Project Structure

```
linkedin_automation/
├── campaigns/
│   ├── views.py         # Handles search + invite logic
│   ├── urls.py          # Campaign-specific routes
│   ├── tasks.py         # Playwright automation scripts
│   └── models.py        # Optional: Track sent invites later
│
├── templates/campaigns/
│   ├── search_form.html
│   ├── results.html
│   ├── confirm_send.html
│   └── success.html
│
├── manage.py
└── linkedin_automation/
    ├── settings.py
    └── urls.py
```

---

## 🧰 Key Files & Functions

### 1. `tasks.py` – Core Automation Logic

#### `run_linkedin_login_and_search(email, password, domain)`
Logs into LinkedIn and searches for people based on domain input.

Returns list of unique public profile URLs.

#### `send_linkedin_invites(email, password, profile_list, domain="AI", message_template=None)`
Sends connection requests to each profile.

Supports custom message templates and shows success/failure status.

---

### 2. `views.py` – Django Integration

Handles:
- User login/register
- Form validation
- Session-based data passing
- Rendering templates with CSRF protection

---

### 3. Templates – Clean UI

All templates use Bootstrap for styling and include proper URL namespacing:

- `search_form.html` – Collects LinkedIn credentials and domain
- `results.html` – Shows extracted profile links
- `confirm_send.html` – Asks user to confirm before sending invites
- `success.html` – Shows how many invites were sent

---

## 📄 Requirements

Make sure you have:

- Python 3.10+
- Django 5.x
- Playwright installed (`pip install playwright`)
- Chromium support (`playwright install chromium`)

---

## 📝 Example `requirements.txt`

```txt
django==5.2.3
playwright==1.52.0
```

---

## 📌 Ethical Use Policy

This project is intended for:
- Personal learning
- Portfolio/demo purposes
- Educational use

🚫 Do NOT use this to spam connections or bypass LinkedIn's ToS.

✅ Always respect LinkedIn’s [Terms of Service](https://www.linkedin.com/legal/terms)

---

## 🎯 Upcoming Improvements

- Store campaign history in database
- Add admin panel to track sent invites
- Build dashboard for stats tracking
- Support CSV/PDF exports of profiles
- Add filters for job title, location, experience level

---

## 📦 License

MIT License – free to modify and share, but do **not** use for unethical activity.

---


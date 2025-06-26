# Service-Now
# Service Now - Vehicle Service Booking App 🚗🔧 (Live Site: https://service-now-1.onrender.com/)

**Service Now** is a Flask-based web application that allows users to register, log in, and book different types of vehicle services — including General Service, Custom Service, and Speed Service. Admins can view all bookings, and users receive confirmation emails upon booking.

---

## 🚀 Features

- 🔐 User authentication (Signup/Login)
- 🛠️ Book General, Speed, and Custom Services
- 📧 Email confirmation on service booking
- 📦 MongoDB for data storage
- 📊 Admin dashboard to view all bookings
- 🎨 Clean and responsive UI using Bootstrap 4
- 🧾 Unique Order ID generation
- 🧹 Session management and flash messaging

---
## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Flask (Python)
- **Database:** MongoDB (MongoDB Atlas)
- **REST API:** Flask routes expose service booking and user operations
- **Mail Service:** Flask-Mail with SMTP
- **Deployment:** Render or any Flask-compatible host


---
## 📁 Folder Structure

ServiceNow/
│
├── app.py # Main Flask app
├── .env # Environment variables
├── requirements.txt # Python dependencies
│
├── static/
│ └── assets/ # Images, favicon
│
├── templates/
│ ├── components/ # HTML components (nav, submit, etc.)
│ ├── index.html # Homepage
│ └── record.html # Booking record form
│
└── README.md # This file

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/service-now.git
   cd service-now
   
Access the app
Open your browser and go to http://localhost:5000

🧪 Future Improvements
Admin panel with authentication
Service status tracking
PDF invoice generation
Payment gateway integration

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

📬 Contact
Developer: Jithendiriyan S S
📧 Email: ssjithendiriyan@gmail.com
📞 Phone: +91 9360206635

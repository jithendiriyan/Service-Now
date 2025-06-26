# ============================
# Flask Web Application
# ============================

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from pymongo import MongoClient
import os, dotenv, datetime, uuid

# ============================
# Load environment variables
# ============================
dotenv.load_dotenv()

# ============================
# Initialize Flask App
# ============================
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ============================
# Mail Configuration
# ============================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('DEL_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('DEL_EMAIL')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# ============================
# MongoDB Configuration
# ============================
url = "mongodb+srv://Jithendiriyan:Jeeva123@cluster0.rkyel8o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(url)
db = client['Service_vehicle_service']
speed_appointments = db['Speed Appointments']
general_appointments = db['General Appointments']
customize_appointments = db['Custom Appointments']
signup_details = db['Signup Details']
orders_collection = db['Orders']

# ============================
# Route: Home Page
# ============================
@app.route('/')
def home():
    return render_template('index.html')

# ============================
# Route: Membership /get In Touch Form
# ============================
@app.route('/get_touch', methods=['GET', 'POST'])
def get_touch():
    if request.method == 'POST':
        plan = request.form.get('plan')
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('number')
        location = request.form.get('location')

        msg = Message(
            subject=f"New Inquiry for {plan}",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"""
            Name: {name}
            Email: {email}
            Phone: {number}
            Location: {location}
            Plan Interested: {plan}
            """
        )
        mail.send(msg)
        flash("Form submitted successfully!", "success")
        return redirect(url_for('submit'))

    return render_template('components/get_touch.html', user=session.get('user'))

# ============================
# Route: Book Order
# ============================
@app.route('/book_order', methods=['GET', 'POST'])
def book_order():
    if 'user' not in session:
        return redirect(url_for('login_Form'))
    return_page = request.args.get('return_page', 'home')
    product = request.args.get('product', '')
    price = int(request.args.get('price', '0'))
    qty = 1
    total_price = price

    if request.method == 'POST':
        qty = int(request.form.get('qty','1'))
        price = int(request.form.get('price','0'))
        total_price = qty * price

        new_order={'product': product,'qty':qty,'price':price,'total_price':total_price}

        if 'orders' not in session or not isinstance(session['orders'], list):            
            session['orders']=[]
        session['orders'].append(new_order)
        session.modified=True
        return redirect(url_for(return_page))
    return render_template('components/book_order.html', user=session['user'], product=product, qty=qty,  price=price, total_price=total_price)

# ============================
# Route: View Cart & Place Order
# ============================
@app.route('/view_cart', methods=['GET', 'POST'])
def view_cart():
    order_id = str(uuid.uuid4())[:10]
    orders = session.get('orders', [])
    grand_total = sum(item['total_price'] for item in orders)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        data = {
            'orderid': order_id,
            'name': name,
            'email': email,
            'phonenumber': phone,
            'address': address,
            'orders': orders,
            'grand_total': grand_total,
            'timestamp': datetime.datetime.now()
        }

        # Send order email
        order_lines = "\n".join(
            [f"{i+1}. Product: {item['product']}, Qty: {item['qty']}, Price: {item['price']}, Total: {item['total_price']}"
             for i, item in enumerate(orders)]
        )

        msg = Message(
            subject="Your Purchase Orders:",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"""
            orderid: {order_id},
            Name: {name},
            Email: {email},
            Phone Number: {phone},
            Address: {address},
            Orders:
            {order_lines},
            Total: {grand_total}
            """
        )
        mail.send(msg)

        session['order_id'] = order_id
        orders_collection.insert_one(data)
        session.pop('orders', None)
        flash('Order Booked successfully!', 'success')
        return redirect(url_for('place_order'))

    return render_template('components/view_cart.html', user=session.get('user'), orderid=order_id, orders=orders, grand_total=grand_total)

# ============================
# Route: Order Placement Confirmation
# ============================
@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    orderid = session.get('order_id')
    return render_template('components/place_order.html', order_Id=orderid)

# ============================
# Route: Order Record Display
# ============================
@app.route('/order_record', methods=['GET', 'POST'])
def order_record():
    user = session.get('user')
    orders = []
    grand_total = 0

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        db_orders  = list(orders_collection.find({'name': name, 'email': email}))

        for order in db_orders:
            timestamp = order.get('timestamp')
            for item in order.get('orders', []):                
                item['order_Id'] = order['orderid'] 
                item['timestamp'] = timestamp   
                orders.append(item)            
        grand_total = sum(item.get('total_price', 0) for item in orders)
    return render_template('components/orders_records.html',user=user,orders=orders,grand_total=grand_total)

# ===== BOOKING's ROUTE ======
# ============================
# Route: Custom Booking 
# ============================

@app.route('/book_customize', methods=['GET', 'POST'])
def book_customize():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('phone')
        location = f"{request.form.get('address1')}, {request.form.get('address2')}, {request.form.get('city')}, {request.form.get('state')} - {request.form.get('zip')}"
        vehicle=f"{request.form.get('vehicle')}, {request.form.get('register_no')}, {request.form.get('make')}, {request.form.get('model')}"
        complain= request.form.get('complain')
        data = {
             'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address1': request.form.get('address1'),
            'address2': request.form.get('address2'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip'),
            'vehicle': request.form.get('vehicle'),
            'register_no': request.form.get('register_no'),
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'distance': request.form.get('distance'),
            'complain' : request.form.get('complain'),
            'check': 'on' if request.form.get('check') else 'off'
        }
        msg = Message(
            subject=f"Service Booking : Custom / Complain",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"""
            Name: {name}
            Email: {email}
            Phone: {number}
            Location: {location}
            Vehicle Details :{vehicle}
            Complain:{complain}
            """
        )
        mail.send(msg) 

        customize_appointments.insert_one(data)
        flash('Booking submitted successfully!', 'success')
        return redirect(url_for('submit_page')) 
    return render_template('components/book.html', user=session.get('user'))

# ============================
# Route: General Booking
# ============================
@app.route('/book_general', methods=['GET', 'POST'])
def book_general():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('phone')
        location = f"{request.form.get('address1')}, {request.form.get('address2')}, {request.form.get('city')}, {request.form.get('state')} - {request.form.get('zip')}"
        vehicle=f"{request.form.get('vehicle')}, {request.form.get('register_no')}, {request.form.get('make')}, {request.form.get('model')}"
        complain= request.form.get('complain')
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address1': request.form.get('address1'),
            'address2': request.form.get('address2'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip'),
            'vehicle': request.form.get('vehicle'),
            'register_no': request.form.get('register_no'),
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'distance': request.form.get('distance'),
            'complain': request.form.get('complain'),
            'check': 'on' if request.form.get('check') else 'off'
        }
        msg = Message(
            subject=f"Service Booking : General",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"""
            Name: {name}
            Email: {email}
            Phone: {number}
            Location: {location}
            Vehicle Details :{vehicle}
            Complain:{complain}
            """
        )
        mail.send(msg) 

        general_appointments.insert_one(data)
        flash('Booking submitted successfully!', 'success')
        return redirect(url_for('submit_page'))  # <-- Fixed
    return render_template('components/book_g.html', user=session.get('user'))

# ============================
# Route: Speed Booking
# ============================
@app.route('/book_speed', methods=['GET', 'POST'])
def book_speed():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        number = request.form.get('phone')
        location = f"{request.form.get('address1')}, {request.form.get('address2')}, {request.form.get('city')}, {request.form.get('state')} - {request.form.get('zip')}"
        vehicle=f"{request.form.get('vehicle')}, {request.form.get('register_no')}, {request.form.get('make')}, {request.form.get('model')}"
        complain= request.form.get('complain')
        time=f"{request.form.get('hours')}, {request.form.get('minutes')}"
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address1': request.form.get('address1'),
            'address2': request.form.get('address2'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip'),
            'vehicle': request.form.get('vehicle'),
            'register_no': request.form.get('register_no'),
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'distance': request.form.get('distance'),
            'complain': request.form.get('complain'),
            'hours': request.form.get('hours'),
            'minutes': request.form.get('minutes'),
            'check': 'on' if request.form.get('check') else 'off'
        }

        msg = Message(
            subject=f"Service Booking : Speed X",
            recipients=[app.config['MAIL_USERNAME']],
            body=f"""
            Name: {name}
            Email: {email}
            Phone: {number}
            Location: {location}
            Vehicle Details :{vehicle}
            Complain:{complain}
            Time:{time}
            """
        )
        mail.send(msg) 

        speed_appointments.insert_one(data)
        flash('Booking submitted successfully!', 'success')
        return redirect(url_for('submit_page'))
    return render_template('components/book_speed.html', user=session.get('user'))
# ============================
# ============================
# Route: OIL FLUID
# ============================
@app.route('/oil_fluid')
def oil_fluid():
    return render_template('components/oil_fluids.html')

@app.route('/spares')
def spares():
    return render_template('components/parts.html')

@app.route('/accessories')
def accessories():
    return render_template('components/accessories.html')

@app.route('/electrical_spares')
def electrical_spares():
    return render_template('components/electrical_spares.html')

# ============================
# Route: SIGNUP
# ============================
@app.route('/signup_Form', methods=['GET', 'POST'])
def signup_Form():
     if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re-password')
        existing_user=signup_details.find_one({'email':email})
        if existing_user:
            flash('Email already registered. Please log in.','danger')
            return redirect(url_for('login_Form'))
        
        if password !=re_password:
            flash('Passwords do not match. Please try again','danger')
            return redirect(url_for('signup_Form'))
        data = {
            'name': request.form.get('name'),
            'email': email,
            'phone': request.form.get('phone'),
            'password':password
        }

        signup_details.insert_one(data)
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login_Form'))
     return render_template('components/signup.html')
 
# ============================
# Route: LOGIN
# ============================
@app.route('/login_Form', methods=['GET', 'POST'])
def login_Form():
    if request.method == 'POST':
        email= request.form.get('email')
        password= request.form.get('password')
        user=signup_details.find_one({'email':email})

        if not user:
            flash('Email not found. Please sign up.', 'danger')
            return redirect(url_for('signup_Form'))
        if user['password'] != password:
            flash('Incorrect password. Try again.', 'danger')
            return redirect(url_for('login_Form'))
        session['user'] = {
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone']
        }
        flash('Login submitted successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('components/login.html')

# ============================
# Route: FORGOT PASSWORD
# ============================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = signup_details.find_one({'email': email})

        if user:
            flash(f"Password reset link sent to {email} (simulation only)", 'info')
        else:
            flash("Email not found!", 'warning')

    return render_template('components/forgot_password.html')

# ============================
# Route: LOGOUT
# ============================

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

# ============================
# Route: SUBMIT PAGE
# ============================

@app.route('/submit', methods=['GET'])
def submit():
    return render_template('components/submit.html')

@app.route('/submit')
def submit_page():
    return render_template('components/submit.html')

# ============================
# Route: SERVICE RECORDS
# ============================
@app.route('/record', methods=['GET', 'POST'])
def record():
    records = []
    searched = False

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        searched = True

        # Search across all collections
        queries = {
            'customize': customize_appointments.find({'name': name, 'email': email}),
            'general': general_appointments.find({'name': name, 'email': email}),
            'speed': speed_appointments.find({'name': name, 'email': email})
        }

        # Combine results
        for key in queries:
            records.extend(list(queries[key]))

    return render_template('components/records.html', records=records, searched=searched, user=session['user'])

# ============================
# Route: PROFILE
# ============================
@app.route('/profile', methods=['GET'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login_Form'))
    return render_template('components/profile.html', user=session['user'])

# ============================
# Route: MEMBERSHIP
# ============================
@app.route('/membership')
def membership():
    return render_template('components/membership.html')

# ============================
# Route: MAIN
# ============================
if __name__ == '__main__':
    app.run(debug=True)
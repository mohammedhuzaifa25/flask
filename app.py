from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registrations.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Database model for registrations
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return f'<Registration {self.name}>'

# Create the database schema
with app.app_context():
    db.create_all()

# Route for the index page
@app.route('/')
def index_page():
    return render_template('index.html')

# Route for the rules page
@app.route('/rules')
def rules_page():
    return render_template('rules.html')

# Route for the registration page
@app.route('/register')
def register_page():
    return render_template('register.html')

# Handle registration form submission
@app.route('/submit-registration', methods=['POST'])
def register():
    try:
        # Collect form data
        name = request.form.get('participantName')
        category = request.form.get('categoryDropdown')
        topic = request.form.get('topicInput')
        email = request.form.get('emailAddress')
        phone = request.form.get('phoneNumber')

        # Validation: Ensure no fields are empty
        if not name or not category or not topic or not email or not phone:
            return jsonify({'error': 'Missing form data! Please fill all fields.'}), 400

        # Ensure uniqueness of email and phone
        existing_email = Registration.query.filter_by(email=email).first()
        existing_phone = Registration.query.filter_by(phone=phone).first()
        if existing_email or existing_phone:
            return jsonify({'error': 'Email or phone number already registered!'}), 409

        # Save data to the database
        new_registration = Registration(
            name=name,
            category=category,
            topic=topic,
            email=email,
            phone=phone
        )
        db.session.add(new_registration)
        db.session.commit()

        # Return success message
        return jsonify({'message': 'Registration Successful!'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred during registration. Please try again later.'}), 500

# Route for the admin panel
@app.route('/admin')
def admin_panel():
    registrations = Registration.query.all()
    return render_template('admin.html', registrations=registrations)

# Error handler for 404
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Page not found'}), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error occurred. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)

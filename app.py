from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vaccination.db'
db = SQLAlchemy(app)

# Define database models
class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    parent_id = db.Column(db.String)
    parent_email = db.Column(db.String)
    gender = db.Column(db.String)
    dob = db.Column(db.Date)
    vaccination_schedules = db.relationship('VaccinationSchedule', backref='child')

class Vaccine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    schedule = db.Column(db.String)

class VaccinationSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    vaccine_id = db.Column(db.Integer, db.ForeignKey('vaccine.id'), nullable=False)
    vaccination_date = db.Column(db.String)

# Create all tables if they don't exist
with app.app_context():
    db.create_all()

    #vaccine schedule
    vaccines = [
    ('BCG', '0 days'),
    ('Hepatitis B', '0 days, 6 weeks, 14 weeks'),
    ('DTaP', '6 weeks, 10 weeks, 14 weeks, 15-18 months, 4-6 years'),
    ('Hib', '6 weeks, 10 weeks, 14 weeks, 15-18 months'),
    ('PCV', '6 weeks, 10 weeks, 14 weeks, 15-18 months'),
    ('IPV', '6 weeks, 10 weeks, 14 weeks, 4-6 years'),
    ('Rotavirus', '6 weeks, 10 weeks, 14 weeks'),
    ('MMR', '12-15 months, 4-6 years'),
    ('Varicella', '12-15 months, 4-6 years')
] 
    for vaccine_data in vaccines:
        vaccine = Vaccine.query.filter_by(name=vaccine_data[0]).first()
        if not vaccine:
            vaccine = Vaccine(name=vaccine_data[0], schedule=vaccine_data[1])
            db.session.add(vaccine)
    db.session.commit()

# Helper function to calculate vaccination dates
def calculate_vaccination_schedule(dob, schedule):
    dates = []
    split_schedule = schedule.split(',')
    for interval in split_schedule:
        interval = interval.strip()
        if 'days' in interval:
            days = int(interval.replace(' days', ''))
            date = dob + timedelta(days=days)
            dates.append(date.strftime('%Y-%m-%d'))
        elif 'weeks' in interval:
            weeks = int(interval.replace(' weeks', ''))
            date = dob + timedelta(weeks=weeks*7)
            dates.append(date.strftime('%Y-%m-%d'))
        elif 'months' in interval:
            months = int(interval.replace(' months', ''))
            date = dob + timedelta(days=months*30)
            dates.append(date.strftime('%Y-%m-%d'))
        elif '-' in interval:
            start, end = interval.split('-')
            start_months = int(start.replace(' ', ''))
            end_months = int(end.replace(' ', ''))
            start_date = dob + timedelta(days=start_months*30)
            end_date = dob + timedelta(days=end_months*30)
            dates.append(f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
    return dates

# Function to send reminder notifications
def send_reminder_notification(parent_id, vaccination_date, vaccine_id):
    parent = Child.query.filter_by(parent_id=parent_id).first()
    parent_email = parent.parent_email
    vaccine = Vaccine.query.get(vaccine_id)
    vaccine_name = vaccine.name

    message = f"Dear Parent,\n\nThis is a reminder that your child's {vaccine_name} vaccination is scheduled for {vaccination_date}.\n\nPlease make sure to visit the vaccination center on the scheduled date.\n\nBest regards,\nImmunization Team"

    # Email server configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "estherchepunton@gmail.com"
    smtp_password = "555"

    msg = MIMEText(message)
    msg['Subject'] = f"Vaccination Reminder: {vaccine_name}"
    msg['From'] = smtp_username
    msg['To'] = parent_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

    print(f"Reminder notification sent to {parent_email} for {vaccine_name} on {vaccination_date}")

# Route for rendering the entry page
@app.route('/')
def entry():
    return render_template('entry.html')

# Route for rendering the display page
@app.route('/display')
def display():
    return render_template('display.html')

# Route for submitting data
@app.route('/submit-data', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        child_name = data['childName']
        parent_id = data['parentId']
        email = data['parentEmail']
        gender = data['gender']
        dob = datetime.strptime(data['dob'], '%Y-%m-%d')

        new_child = Child(name=child_name, parent_id=parent_id, parent_email=email, gender=gender, dob=dob)
        db.session.add(new_child)
        db.session.commit()

        child_id = new_child.id

        vaccine_schedules = []
        vaccines = Vaccine.query.all()
        for vaccine in vaccines:
            vaccination_dates = calculate_vaccination_schedule(dob, vaccine.schedule)
            for date in vaccination_dates:
                new_schedule = VaccinationSchedule(child_id=child_id, vaccine_id=vaccine.id, vaccination_date=date)
                db.session.add(new_schedule)
                # Send reminder notification
                send_reminder_notification(parent_id, date, vaccine.id)
            vaccine_schedules.append({
                'vaccine_id': vaccine.id,
                'dates': vaccination_dates
            })

        db.session.commit()

        return jsonify({'message': 'Data submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for getting data
@app.route('/get-data', methods=['GET'])
def get_data():
    children = Child.query.all()
    child_data = []
    for child in children:
        vaccination_schedule = [schedule.vaccination_date for schedule in child.vaccination_schedules]
        child_data.append({
            'name': child.name,
            'parentId': child.parent_id,
            'parentEmail': child.parent_email,
            'gender': child.gender,
            'dob': child.dob.strftime('%Y-%m-%d'),
            'vaccinationSchedule': vaccination_schedule
        })

    return jsonify(child_data), 200

if __name__ == '__main__':
    app.run(debug=True)

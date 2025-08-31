

import os
import csv
import json
import smtplib
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import uuid
import time

# Import scraper functions
from facebook_scraper import run_facebook_scraper
from instagram_scraper import run_instagram_scraper
from x_scraper import run_x_scraper

app = Flask(__name__)
app.secret_key = 'Flask@7867'  # Change this in production

# Dictionary to store scraping status for each user session
user_sessions = {}
# Lock for thread-safe access to user_sessions
sessions_lock = threading.Lock()

# Configuration
MAX_CONCURRENT_OPERATIONS = 15
SESSION_TIMEOUT = 3600  # 1 hour in seconds


def get_user_session():
    """Get or create user session data"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session.permanent = True

    user_id = session['user_id']

    with sessions_lock:
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'status': 'idle',
                'message': '',
                'csv_file': '',
                'platform': '',
                'target': '',
                'limit': 0,
                'record_count': 0,
                'created_at': time.time()
            }

    return user_id, user_sessions[user_id]


def cleanup_old_sessions():
    """Clean up old inactive sessions"""
    current_time = time.time()
    with sessions_lock:
        expired_sessions = [
            user_id for user_id, data in user_sessions.items()
            if current_time - data.get('created_at', 0) > SESSION_TIMEOUT
        ]

        for user_id in expired_sessions:
            # Clean up CSV file if exists
            if user_sessions[user_id].get('csv_file') and os.path.exists(user_sessions[user_id]['csv_file']):
                try:
                    os.remove(user_sessions[user_id]['csv_file'])
                except:
                    pass

            del user_sessions[user_id]
            print(f"Cleaned up expired session: {user_id}")


def get_active_operations_count():
    """Count currently active scraping operations"""
    with sessions_lock:
        return sum(1 for data in user_sessions.values() if data['status'] == 'processing')


@app.route('/')
def index():
    # Trigger session creation and cleanup
    get_user_session()
    cleanup_old_sessions()
    return render_template('index.html')


@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    user_id, user_status = get_user_session()

    data = request.json
    platform = data.get('platform', '').lower()
    target = data.get('target', '')
    limit = int(data.get('limit', 10))

    # Validate input
    if not platform or not target or limit <= 0:
        return jsonify({'success': False, 'error': 'Invalid input parameters'})

    # Check if user already has an operation running
    if user_status['status'] == 'processing':
        return jsonify({'success': False, 'error': 'You already have a scraping operation in progress'})

    # Check concurrent operations limit
    if get_active_operations_count() >= MAX_CONCURRENT_OPERATIONS:
        return jsonify({'success': False, 'error': 'Server is busy. Please try again later.'})

    # Update user status
    with sessions_lock:
        user_sessions[user_id].update({
            'status': 'processing',
            'message': 'Scraping in process',
            'csv_file': '',
            'platform': platform,
            'target': target,
            'limit': limit,
            'record_count': 0,
            'created_at': time.time()
        })

    # Start scraping in background thread
    thread = threading.Thread(target=run_scraper, args=(user_id, platform, target, limit))
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'Scraping started'})


def run_scraper(user_id, platform, target, limit):
    """Run scraper for specific user"""
    try:
        csv_filename = None

        if platform == "facebook":
            csv_filename = run_facebook_scraper(target, limit)
        elif platform == "instagram":
            csv_filename = run_instagram_scraper(target, limit)
        elif platform in ["twitter", "twitter/x", "x"]:
            csv_filename = run_x_scraper(target, limit)
        else:
            raise ValueError(f"Unknown platform: {platform}")

        # Count records in CSV
        record_count = 0
        if csv_filename and os.path.exists(csv_filename):
            with open(csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                record_count = sum(1 for row in reader) - 1  # Subtract header row

        # Update user status
        with sessions_lock:
            if user_id in user_sessions:  # Check if session still exists
                user_sessions[user_id].update({
                    'status': 'completed',
                    'message': f'Successfully extracted {record_count} records',
                    'csv_file': csv_filename,
                    'record_count': record_count,
                    'created_at': time.time()
                })

    except Exception as e:
        # Update user status with error
        with sessions_lock:
            if user_id in user_sessions:  # Check if session still exists
                user_sessions[user_id].update({
                    'status': 'error',
                    'message': f'Error occurred during extraction: {str(e)}',
                    'csv_file': '',
                    'record_count': 0,
                    'created_at': time.time()
                })


@app.route('/get_status')
def get_status():
    user_id, user_status = get_user_session()
    return jsonify(user_status)


@app.route('/view_data')
def view_data():
    user_id, user_status = get_user_session()

    if not user_status['csv_file'] or not os.path.exists(user_status['csv_file']):
        return jsonify({'success': False, 'error': 'No data file found'})

    try:
        csv_data = []
        with open(user_status['csv_file'], 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            csv_data = list(reader)

        return jsonify({
            'success': True,
            'headers': csv_data[0] if csv_data else [],
            'rows': csv_data[1:] if len(csv_data) > 1 else []
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/download_csv')
def download_csv():
    user_id, user_status = get_user_session()

    if not user_status['csv_file'] or not os.path.exists(user_status['csv_file']):
        return jsonify({'error': 'No file available for download'}), 404

    filename = f"extracted_data_{user_status['platform']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return send_file(
        user_status['csv_file'],
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )


@app.route('/send_email', methods=['POST'])
def send_email():
    user_id, user_status = get_user_session()

    if not user_status['csv_file'] or not os.path.exists(user_status['csv_file']):
        return jsonify({'success': False, 'error': 'No file available to send'})

    data = request.json
    sender_email = data.get('sender_email', '')
    sender_password = data.get('sender_password', '')
    recipient_email = data.get('recipient_email', '')
    smtp_server = data.get('smtp_server', 'smtp.gmail.com')
    smtp_port = int(data.get('smtp_port', 587))

    if not all([sender_email, sender_password, recipient_email]):
        return jsonify({'success': False, 'error': 'Please fill in all email fields'})

    # Send email in background thread with user-specific data
    thread = threading.Thread(
        target=send_email_smtp,
        args=(user_id, sender_email, sender_password, recipient_email, smtp_server, smtp_port)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'Email is being sent...'})


def send_email_smtp(user_id, sender_email, sender_password, recipient_email, smtp_server, smtp_port):
    """Send email with user-specific data"""
    try:
        # Get user status at time of sending
        with sessions_lock:
            if user_id not in user_sessions:
                print(f"User session {user_id} not found for email sending")
                return
            user_status = user_sessions[user_id].copy()

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Scraped Data from {user_status['platform'].title()}"

        # Email body
        body = f"""Hello,

Please find attached the scraped data from {user_status['platform'].title()}.

Scraping Details:
- Platform: {user_status['platform'].title()}
- Target: {user_status['target']}
- Limit: {user_status['limit']}
- Records: {user_status['record_count']}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Multi-Platform Scraper Tool
"""

        msg.attach(MIMEText(body, 'plain'))

        # Attach CSV file
        if user_status['csv_file'] and os.path.exists(user_status['csv_file']):
            with open(user_status['csv_file'], "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(user_status["csv_file"])}'
            )
            msg.attach(part)

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print(f"Email sent successfully for user {user_id}")

    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication Error for user {user_id}: {str(e)}")
    except Exception as e:
        print(f"Email Error for user {user_id}: {str(e)}")


@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Allow user to reset their session if stuck"""
    user_id, user_status = get_user_session()

    with sessions_lock:
        if user_id in user_sessions:
            # Clean up CSV file if exists
            if user_status.get('csv_file') and os.path.exists(user_status['csv_file']):
                try:
                    os.remove(user_status['csv_file'])
                except:
                    pass

            # Reset to idle state
            user_sessions[user_id].update({
                'status': 'idle',
                'message': '',
                'csv_file': '',
                'platform': '',
                'target': '',
                'limit': 0,
                'record_count': 0,
                'created_at': time.time()
            })

    return jsonify({'success': True, 'message': 'Session reset successfully'})


# Cleanup old sessions periodically
@app.before_request
def before_request():
    # Clean up old sessions on every 50th request to avoid overhead
    if hash(request.endpoint) % 50 == 0:
        cleanup_old_sessions()


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway provides $PORT
    print("Using port:", os.environ.get("PORT"))

    app.run(host="0.0.0.0", port=port, debug=True)


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import configparser

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Email Configuration
SENDER_EMAIL = config['EMAIL']['sender_email']
SUBJECT = config['EMAIL']['subject']

# Load email message template from message_template.html
def load_message_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Load customer data from customers.txt
def load_customers(file_path):
    customers = []
    with open(file_path, 'r') as file:
        for line in file:
            name, email = line.strip().split(',')
            customers.append({"name": name, "email": email})
    return customers

# Get SMTP configurations from config.ini
def get_smtp_configs():
    smtp_configs = []
    for section in config.sections():
        if section.startswith('SMTP'):
            smtp_config = {
                'server': config[section]['server'],
                'port': int(config[section]['port']),
                'username': config[section]['username'],
                'password': config[section]['password']
            }
            smtp_configs.append(smtp_config)
    return smtp_configs

# Send email using a specific SMTP configuration
def send_email(to_email, name, smtp_config, message_template):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = SUBJECT

        # Personalize the message
        body = message_template.replace('{name}', name)
        msg.attach(MIMEText(body, 'html'))

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        
        print(f"Email sent to {to_email} using {smtp_config['server']}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Send emails in batches using multiple SMTP configurations
def send_emails_in_batches(customers, batch_size, message_template):
    smtp_configs = get_smtp_configs()
    smtp_index = 0  # Start with the first SMTP configuration

    for i in range(0, len(customers), batch_size):
        batch = customers[i:i + batch_size]
        smtp_config = smtp_configs[smtp_index]  # Use the current SMTP configuration

        for customer in batch:
            send_email(customer['email'], customer['name'], smtp_config, message_template)
        
        # Switch to the next SMTP configuration
        smtp_index = (smtp_index + 1) % len(smtp_configs)
        
        # Wait for a few seconds before sending the next batch
        if i + batch_size < len(customers):
            print(f"Switching to SMTP: {smtp_configs[smtp_index]['server']}")
            print(f"Waiting for 60 seconds before sending the next batch...")
            time.sleep(60)

if __name__ == "__main__":
    # Load customers from customers.txt
    customers = load_customers('customers.txt')
    
    # Load message template from message_template.html
    message_template = load_message_template('message_template.html')
    
    # Set batch size
    BATCH_SIZE = 40
    
    # Send emails
    send_emails_in_batches(customers, BATCH_SIZE, message_template)

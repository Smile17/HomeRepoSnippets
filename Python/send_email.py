import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up the email content
email = MIMEMultipart()
email['Subject'] = 'Test email'
email['From'] = 'mtvkatya@gmail.com'
email['To'] = 'mtvkatya@gmail.com'
body = 'This is a test email.'
email.attach(MIMEText(body, 'plain'))

# Set up the SMTP server
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'mtvkatya@gmail.com'
smtp_password = 'C044f33pXLZdB21Vby0Xsyb1'

# Connect to the SMTP server and send the email
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, email['To'], email.as_string())
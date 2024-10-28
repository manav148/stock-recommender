import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_email_content(stock_results):
    email_content = "Stock Recommendations:\n\n"
    table_content = "| Stock | Recommendation |\n|-------|----------------|\n"
    detailed_content = "\nDetailed Recommendations:\n\n"

    for stock, result in stock_results.items():
        recommendation = result.split('\n')[0].strip()  # Assuming the recommendation is the first line
        table_content += f"| {stock} | {recommendation} |\n"
        detailed_content += f"{stock}:\n{result}\n\n"

    email_content += table_content + detailed_content
    return email_content

def send_email(to_email, subject, body):
    # Replace these with your email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "your_email@gmail.com"
    smtp_password = "your_email_password"

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
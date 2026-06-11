import smtplib
from email.message import EmailMessage
from config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT


def send_email_alert(to_email, subject, body, attachment_path=None):
    if not SMTP_EMAIL or not SMTP_PASSWORD or not to_email:
        return False

    try:
        msg = EmailMessage()
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment_path:
            with open(attachment_path, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="image",
                    subtype="jpeg",
                    filename=attachment_path.split("/")[-1].split("\\")[-1]
                )

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print("Email failed:", e)
        return False

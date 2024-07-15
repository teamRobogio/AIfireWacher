import cv2
import base64
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from openai import OpenAI

# Hard-code the API key directly
api_key = "YOUR API KEY"
client = OpenAI(api_key=api_key)

# Email configuration
EMAIL_ADDRESS = "giorgiocorrado@gmail.com"
EMAIL_PASSWORD = "tqja kiap oepl enyi"
EMAIL_RECIPIENT = "giorgiocorrado@gmail.com"

def classify_response(response):
    prompt = f"The following is a response from a fire monitoring system. Does it indicate the presence of fire at that point in time, flames, burning, smoke, sparks, conflagration or ignition? Respond with 'yes' or 'no' only:\n\n\"{response}\"" # Craft prompt to detect fire
    PROMPT_MESSAGES = [
        {"role": "system", "content": "You are a fire detection classifier only 'yes' or 'no' as responses nothing else. always lower capital letter no matter what"},
        {"role": "user", "content": prompt}
    ]
    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 50,
    }

    # Send request to GPT
    result = client.chat.completions.create(**params)
    description = result.choices[0].message.content.strip().lower()
    print(f"Description: {description}")
    return description == "yes"

def send_email(subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(attachment_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")

    msg.attach(part)
    attachment.close()

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_RECIPIENT, text)

def activate_action_if_fire(response, frame, description):
    if classify_response(response):
        print("Action Activated: Fire detected!")

        # Save the frame
        timestamp = int(time.time())
        frame_filename = f"frame_{timestamp}.jpg"
        cv2.imwrite(frame_filename, frame)

        # Save the description and alert
        alert_info = f"Description: {description}\nAlert: Fire detected!"

        # Send an email with the info
        send_email("Fire Alert", alert_info, frame_filename)
    else:
        print("No fire detected. No action taken.")

# Open the default camera
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Error: Could not open video.")
    exit()

while True:
    success, frame = video.read()
    if not success:
        print("Error: Could not read frame.")
        break

    _, buffer = cv2.imencode(".jpg", frame)
    base64_frame = base64.b64encode(buffer).decode("utf-8")

    # Craft prompt to detect fire
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "You are a surveillance system. Your job is to prevent fire. Is there any fire, smoke, or other things that can initiate fire, in this frame from a live camera feed? If yes, where is it located? give a description of what you see specifically if there is fire or smoke and tell me where. Limit your answer to 50 words and prioritize fire or smoke if detected.",
                {"image": base64_frame, "resize": 768},
            ],
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 50,
    }

    # Send request to GPT
    result = client.chat.completions.create(**params)
    description = result.choices[0].message.content
    print(f"Description: {description}")

    # Use the description to activate the action if needed
    activate_action_if_fire(description, frame, description)

    # Display the frame
    cv2.imshow('Live Feed', frame)

    # Exit when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Wait a bit before capturing the next frame
    time.sleep(1)

# Release the video capture object and close windows
video.release()
cv2.destroyAllWindows()


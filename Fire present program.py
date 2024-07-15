import cv2
import base64
import time
import requests
from openai import OpenAI

# Hard-code the API key directly
api_key = "YOUR KEY"
client = OpenAI(api_key=api_key)

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
                "Is there any fire in this frame from a live camera feed? If yes, where is it located? Only respond with 'Yes, fire present at [location]' or 'No fire present'.",
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

    # Print the fire presence information only
    if "fire" in description.lower():
        if "no fire" in description.lower():
            print("No fire present")
        else:
            # Extract location from the description
            fire_location = description.split(" at ")[-1]
            print(f"Fire present at {fire_location.strip()}")
    else:
        print("No fire present")

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


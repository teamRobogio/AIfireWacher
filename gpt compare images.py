from IPython.display import Image, display, Audio, Markdown
from openai import OpenAI
import base64
import os
import tkinter as tk
from tkinter import filedialog, Text
from tkinter.scrolledtext import ScrolledText

# Set the API key and model name
MODEL = "gpt-4o"
api_key = "YOUR API KEY"
client = OpenAI(api_key=api_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def upload_image(image_label):
    file_path = filedialog.askopenfilename()
    if file_path:
        encoded_image = encode_image(file_path)
        image_label.config(text=f"Image Path: {file_path}")
        image_label.image_path = file_path  # Store the file path in the label widget
        image_label.encoded_image = encoded_image  # Store the encoded image in the label widget
        return encoded_image
    return None

def upload_image1():
    upload_image(image_label1)

def upload_image2():
    upload_image(image_label2)

def submit_prompt():
    prompt = prompt_entry.get("1.0", tk.END).strip()
    base64_image1 = image_label1.encoded_image  # Retrieve the encoded image from the label widget
    base64_image2 = image_label2.encoded_image  # Retrieve the encoded image from the label widget
    if base64_image1 and base64_image2 and prompt:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image1}"}
                    },
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image2}"}
                    }
                ]}
            ],
            temperature=0.0,
        )
        result = response.choices[0].message.content
        result_text.config(state=tk.NORMAL)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, result)
        result_text.config(state=tk.DISABLED)

# GUI setup
root = tk.Tk()
root.title("Image Comparison GUI")

frame = tk.Frame(root)
frame.pack(pady=10)

image_label1 = tk.Label(frame, text="No image 1 selected")
image_label1.pack()

upload_button1 = tk.Button(frame, text="Upload Image 1", command=upload_image1)
upload_button1.pack(pady=5)

image_label2 = tk.Label(frame, text="No image 2 selected")
image_label2.pack()

upload_button2 = tk.Button(frame, text="Upload Image 2", command=upload_image2)
upload_button2.pack(pady=5)

prompt_label = tk.Label(frame, text="What do you want to detect in the images?")
prompt_label.pack(pady=5)

prompt_entry = ScrolledText(frame, height=5, width=50)
prompt_entry.pack(pady=5)

submit_button = tk.Button(frame, text="Submit", command=submit_prompt)
submit_button.pack(pady=10)

result_text = ScrolledText(frame, height=10, width=50, state=tk.DISABLED)
result_text.pack(pady=5)

root.mainloop()


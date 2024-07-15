
from openai import OpenAI

# Hard-code the API key directly
api_key = "YOUR API KEY"
client = OpenAI(api_key=api_key)

def classify_response(response):
    prompt = f"The following is a response from a fire monitoring system. Does it indicate the presence of fire at that point in time, flames, burning, smoke, sparks, conflagration or ignition ? Respond with 'yes' or 'no' only:\n\n\"{response}\""# Craft prompt to detect fire
    PROMPT_MESSAGES = [
        {"role": "system", "content": "You are a fire prevention detection classifier only 'yes' or 'no' as responses nothing else. always lower capital letter no matter what"},
        {"role": "user", "content": prompt}
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
    return description == "yes"

# Function to activate action if fire is detected
def activate_action_if_fire(response):
    if classify_response(response):
        print("Action Activated: Fire detected!")
    else:
        print("No fire detected. No action taken.")

# Example usage
responses = [
    "There looks like there is vapor, not fire or smoke.",
    "There is a significant amount of smoke and flames visible.",
    "I see sparks but no fire yet.",
    "There was fire but now it stopped.",
    "The area is clear, no signs of fire or smoke.",
    "There is a blaze, and it's spreading quickly!"
]

for response in responses:

    print(f"Response: {response}")
    activate_action_if_fire(response)
    print("\n")

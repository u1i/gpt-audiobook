import openai
import sys
import os
from gtts import gTTS
import datetime
import json

# Read OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    print("Error: The OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

def generate_story(prompt):
    request_prompt = f"""
    You are a creative story writer. Given the following prompt, write a story and provide the title and the story in a JSON object format.
    
    Prompt: "{prompt}"
    
    Respond strictly in the following format:
    {{
        "title": "Title of the Story",
        "story": "The complete story text"
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Consider using "gpt-3.5-turbo" if GPT-4 is not accessible
        messages=[
            {"role": "system", "content": "You are a creative story writer."},
            {"role": "user", "content": request_prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    story_content = response['choices'][0]['message']['content'].strip()
    
    # For debugging purposes, print the raw response
    print("Raw API response:")
    print(story_content)

    # Try to find the JSON object in the response
    try:
        start_idx = story_content.index('{')
        end_idx = story_content.rindex('}') + 1
        json_content = story_content[start_idx:end_idx]
        
        # Clean up JSON content if necessary
        json_content = json_content.replace('\n','').replace('\r','')
        
        # Ensure quotes are properly formatted
        json_content = json_content.replace('“', '"').replace('”', '"').replace('‘', '\'').replace('’', '\'')
        
        # Parse JSON content
        story_json = json.loads(json_content)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON response: {e}")
        sys.exit(1)
    
    return story_json

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_audiobook.py \"<prompt>\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    print("Generating story...")
    story_data = generate_story(prompt)
    
    title = story_data.get("title", "untitled").strip()
    story = story_data.get("story", "").strip()
    
    sanitized_title = "_".join(title.split()).lower()
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    unique_id = os.urandom(4).hex()
    base_filename = f"{sanitized_title}-{timestamp}-{unique_id}"

    text_filename = f"{base_filename}.txt"
    audio_filename = f"{base_filename}.mp3"

    print("Saving story to text file...")
    with open(text_filename, 'w') as text_file:
        text_file.write(story)
    
    print("Converting text to speech...")
    text_to_speech(story, audio_filename)

    print(f"Audiobook saved as {audio_filename}")
    print(f"Text file saved as {text_filename}")

if __name__ == "__main__":
    main()

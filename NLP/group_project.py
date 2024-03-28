import streamlit as st
from langchain import OpenAI
import json
import re

# Initialize the OpenAI API key
client = OpenAI(
    api_key='#',
    organization='#'
)


# Initialize variables
highlighted_text = ""
sentiment = ""
modified_text = ""

# Initialize session state variables
if 'sentiment' not in st.session_state:
    st.session_state['sentiment'] = ""
if 'highlighted_text' not in st.session_state:
    st.session_state['highlighted_text'] = ""

def process_response(response_str):
    try:
        # Parse the string response into a dictionary
        response = json.loads(response_str)

        # Rest of the code from the previous example
        sentiment_counts = {}
        highlighted_text_parts = []

        for sentiment, phrases in response.items():
            for phrase in phrases:
                # Update sentiment counts
                if sentiment not in sentiment_counts:
                    sentiment_counts[sentiment] = 0
                sentiment_counts[sentiment] += 1

                # Prepare highlighted text
                if sentiment != "neutral":  # Ignore neutral sentiments
                    highlighted_phrase = f"{phrase} ({sentiment})"
                else:
                    highlighted_phrase = phrase

                highlighted_text_parts.append(highlighted_phrase)
            
    except json.JSONDecodeError:
        print("Error decoding the JSON response")
        return "Error", "Invalid response"

    # Determine the most common sentiment
    overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)

    # Combine highlighted text parts
    highlighted_text = ", ".join(highlighted_text_parts)

    return overall_sentiment, highlighted_text

def highlight_words(text):
    if not isinstance(text, str):
        return ""  # Return an empty string if text is not a string
    # Process the text to highlight words
    return re.sub(r'\[(\w+)\]', r'<span style="color: orange;">\1</span>', text)


def analyze_sentiment(text):
    # Call OpenAI API to analyze sentiment
    model = "gpt-4-1106-preview"
    response_format = { "type": "json_object"}
    messages = [
        {"role": "system", "content": "You need to determine the sentiment of a text the user inputs about the climate. The sentiment can be the following:"},
        {"role": "system", "content": "admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise, neutral"},
        { "role": "system", "content": "Analyze the following text. The words containing sentiment need to be labeled, you can ignore neutral words, don't label them and don't send them back. Only highlight words that are important sentiment value to humans. The rest needs to be returned in a dictonary format in JSON."},
        {"role": "user", "content": text}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=0.3,
        )

        #print(response)

        # Extract sentiment and highlighted text from the response
        sentiment, highlighted_text = process_response(response.choices[0].message.content)

        return sentiment, highlighted_text
    except Exception as e:
        print(e)
        print(e.__cause__)
        print(e.__context__)
        print(e.__traceback__)
        return "Error", "No text available"


def modify_text(original_text, new_sentiment, highlighted_text):
    model = "gpt-4-1106-preview"
    response_format = { "type": "json_object"}
    messages = [
        {"role": "system", "content": "You need to modify the text the user inputs about the climate. The sentiment of the text needs to be changed to the following:"},
        {"role": "system", "content": new_sentiment},
        { "role": "system", "content": "You classified the original text as the following sentiment:"},
        { "role": "system", "content": highlighted_text },
        { "role": "system", "content": "Modify the following text. The words containing sentiment need to be labeled, you can ignore neutral words, don't label them and don't send them back. Only highlight words that are important sentiment value to humans, put the modified words in []. The rest needs to be returned in a dictonary format in JSON."},
        {"role": "user", "content": original_text}
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=0.5,
        )

        # Directly extract the modified text from the response
        modified_text = json.loads(response.choices[0].message.content)
        #modified_text = modified_text_json.get("modified_text", "No modified text available")
        print(modified_text)

        return modified_text
    
    except Exception as e:
        print(e)
        return "Error"
    

# Streamlit app layout
st.title("Sentiment Analysis and Modification App")

# Text input
user_input = st.text_area("Enter your text test:", height=150)

# Sentiment labels
sentiment_labels = {
    0: 'admiration', 1: 'amusement', 2: 'anger', 3: 'annoyance', 4: 'approval', 5: 'caring',
    6: 'confusion', 7: 'curiosity', 8: 'desire', 9: 'disappointment', 10: 'disapproval',
    11: 'disgust', 12: 'embarrassment', 13: 'excitement', 14: 'fear', 15: 'gratitude',
    16: 'grief', 17: 'joy', 18: 'love', 19: 'nervousness', 20: 'optimism', 21: 'pride',
    22: 'realization', 23: 'relief', 24: 'remorse', 25: 'sadness', 26: 'surprise', 27: 'neutral'
}
# Analyze sentiment button
if st.button("Analyze Sentiment"):
    st.session_state['sentiment'], st.session_state['highlighted_text'] = analyze_sentiment(user_input)
    st.write("Sentiment: ", st.session_state['sentiment'])
    st.write("Highlighted Text: ", st.session_state['highlighted_text'])

# Select box for new sentiment
new_sentiment = st.selectbox("Choose a new sentiment:", list(sentiment_labels.values()))

# Modify text button
if st.button("Modify Text"):
    modified_text = modify_text(user_input, new_sentiment, st.session_state['highlighted_text'])
    st.write("Original Text: ", user_input)
    st.write("Original Sentiment: ", st.session_state['sentiment'])
    print("Modified Text: ", modified_text)
    highlighted_text = highlight_words(modified_text)
    print("Highlighted Text: ", highlighted_text)
    st.markdown("Modified Text:", unsafe_allow_html=True)
    st.markdown(highlighted_text, unsafe_allow_html=True)
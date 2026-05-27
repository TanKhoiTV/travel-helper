# Building MyTravelHelper: A Learning Journey with Streamlit and Hugging Face Inference Providers

This notebook documents the end-to-end process of building **MyTravelHelper**, an AI-powered travel assistant. 
We will explore how to leverage Hugging Face's serverless Inference Providers to perform advanced Natural Language Processing (NLP) tasks without hosting our own models.

### Learning Objectives:
1. Understand Hugging Face Inference Providers and their integration.
2. Explore HF tasks: Text Classification, Zero-Shot Classification, Token Classification.
3. Utilize the Hugging Face Hub Python Library for model discovery.
4. Manage HF free tier resources, billing, and error handling.
5. Deploy a Streamlit app on Hugging Face Spaces.


```python
!pip install -q huggingface_hub streamlit python-dotenv pandas plotly
```


```python
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from a local .env file
load_dotenv()

# Retrieve token
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("⚠️ Warning: HF_TOKEN not found. Please ensure it is set in your environment.")
else:
    print("✅ HF_TOKEN successfully loaded.")

# Initialize the client
client = InferenceClient(api_key=HF_TOKEN)
```

## Section 1: Customer Satisfaction Analytics (Sentiment Analysis)

In this section, we solve **Requirement 1**: Analyzing user reviews to determine their experience (good, satisfied, bad, disappointed).
We use the **Text Classification** task with a model fine-tuned on sentiment analysis.


```python
import time

def analyze_sentiment_with_latency(text: str, model_id: str = "distilbert-base-uncased-finetuned-sst-2-english"):
    start_time = time.time()
    try:
        response = client.text_classification(text=text, model=model_id)
        latency = time.time() - start_time
        
        # Format results
        results = {item.label: item.score for item in response}
        results["latency_seconds"] = round(latency, 3)
        return results
    except Exception as e:
        return {"error": str(e), "latency_seconds": round(time.time() - start_time, 3)}

# Test with positive and negative reviews
positive_review = "The tour guide was exceptionally knowledgeable and the views were breathtaking!"
negative_review = "The hotel room smelled like mold and the air conditioning was broken."

print("Positive Review:", analyze_sentiment_with_latency(positive_review))
print("Negative Review:", analyze_sentiment_with_latency(negative_review))
```

## Section 2: Detecting Topics Mentioned in Reviews

Here we solve **Requirement 3**: Identifying specific topics mentioned in user reviews (e.g., food, service, cleanliness, price).
We use **Zero-Shot Classification**, which allows us to define custom labels on the fly without retraining the model.


```python
def detect_topics(text: str, candidate_topics: list, multi_label: bool = True):
    try:
        response = client.zero_shot_classification(
            text=text,
            labels=candidate_topics,
            multi_label=multi_label,
            model="facebook/bart-large-mnli"
        )
        # Format results
        return {item['label']: round(item['score'], 4) for item in response}
    except Exception as e:
        return {"error": str(e)}

# Test topic detection
sample_review = "The breakfast buffet had a great selection, but the room was quite expensive for what it offered."
travel_topics = ["cleanliness", "food & dining", "customer service", "pricing", "location"]

print("Detected Topics:")
for topic, score in detect_topics(sample_review, travel_topics).items():
    print(f"- {topic}: {score * 100:.2f}%")
```

## Section 3: Analyzing Travel Intention and Object Extraction

Here we solve **Requirement 2**: Analyzing travel intention and performing "object extraction" (Named Entity Recognition) from user-supplied data.
*   **Travel Intention**: Determined via Zero-Shot Classification.
*   **Object Extraction**: Performed via Token Classification to extract locations, dates, and organizations.


```python
def analyze_travel_intent(text: str):
    intentions = ["leisure vacation", "business trip", "family visit", "adventure travel"]
    try:
        response = client.zero_shot_classification(
            text=text,
            labels=intentions,
            multi_label=False,
            model="facebook/bart-large-mnli"
        )
        return response[0]['label']  # Return the top intention
    except Exception as e:
        return f"Error: {str(e)}"

def extract_travel_objects(text: str):
    try:
        response = client.token_classification(
            text=text,
            model="dbmdz/bert-large-cased-finetuned-conll03-english"
        )
        # Group entities for cleaner output
        extracted = {}
        for item in response:
            entity_type = item.get("entity_group") or item.get("entity")
            word = item.get("word")
            if entity_type not in extracted:
                extracted[entity_type] = []
            extracted[entity_type].append(word)
        return extracted
    except Exception as e:
        return {"error": str(e)}

# Test query
user_query = "I need to book a flight to Tokyo for the upcoming tech conference in June, flying with Japan Airlines."
print("Intended Trip Type:", analyze_travel_intent(user_query))
print("Extracted Entities:", extract_travel_objects(user_query))
```

## Section 4: Streamlit App Architecture & Deployment Guide

To turn these prototypes into a polished, interactive web application, we will build a Streamlit app (`app.py`) and deploy it to Hugging Face Spaces.

### Step-by-Step Deployment to Hugging Face Spaces:
1. **Create a Hugging Face Account**: Go to [huggingface.co](https://huggingface.co) and sign up.
2. **Create a New Space**: Click on your profile picture -> **New Space**.
3. **Configure Space Settings**:
   - **Space Name**: `MyTravelHelper`
   - **SDK**: **Streamlit**
   - **Space Hardware**: **CPU Basic (Free)**
4. **Add Secrets**: Go to the Space's **Settings** tab -> **Variables and secrets** -> Add a new secret named `HF_TOKEN` with your Hugging Face Access Token as the value.
5. **Upload Files**: Upload your `app.py` and a `requirements.txt` file containing:
   ```text
   streamlit
   huggingface_hub
   pandas
   plotly
   python-dotenv
   ```

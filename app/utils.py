import os
import time
import random
from huggingface_hub import InferenceClient, InferenceTimeoutError
from huggingface_hub.errors import HfHubHTTPError
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(api_key=os.getenv("HF_TOKEN"))

ERROR_MESSAGES = {
    401: "Authentication failed. Check your HF_TOKEN.",
    403: "Access denied. Request model access on Hugging Face Hub.",
    404: "Model not found. Verify the model ID.",
    429: "Rate limit exceeded. Please wait before retrying.",
    503: "Service temporarily unavailable. Model may be loading.",
}

def _get_error_message(status_code: int) -> str:
    return ERROR_MESSAGES.get(status_code, f"Unexpected error (status {status_code}).")

def _should_retry(status_code: int) -> bool:
    return status_code in (429, 503)

def _call_with_retry(func, *args, max_retries=5, base_delay: float = 1, max_delay: float = 60, **kwargs):
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except HfHubHTTPError as e:
            status_code = e.response.status_code
            if not _should_retry(status_code) or attempt == max_retries - 1:
                return {"error": _get_error_message(status_code)}
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.5)
            time.sleep(delay + jitter)
        except InferenceTimeoutError:
            if attempt == max_retries - 1:
                return {"error": "Request timed out. The model may be overloaded."}
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.5)
            time.sleep(delay + jitter)
        except Exception as e:
            return {"error": str(e)}
    return {"error": _get_error_message(500)}

def analyze_sentiment(text: str) -> dict:
    result = _call_with_retry(
        client.text_classification,
        text=text,
        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return {item.label: item.score for item in result}

def detect_topics(text: str, candidate_topics: list, multi_label: bool = True) -> dict:
    result = _call_with_retry(
        client.zero_shot_classification,
        text=text,
        candidate_labels=candidate_topics,
        multi_label=multi_label,
        model="facebook/bart-large-mnli",
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return {item['label']: item['score'] for item in result}

def analyze_travel_intent(text: str) -> str:
    intentions = ["leisure vacation", "business trip", "family visit", "adventure travel"]
    result = _call_with_retry(
        client.zero_shot_classification,
        text=text,
        candidate_labels=intentions,
        multi_label=False,
        model="facebook/bart-large-mnli",
    )
    if isinstance(result, dict) and "error" in result:
        return f"Error: {result['error']}"
    return result[0]['label']

def extract_travel_objects(text: str) -> dict:
    result = _call_with_retry(
        client.token_classification,
        text=text,
        model="dbmdz/bert-large-cased-finetuned-conll03-english",
    )
    if isinstance(result, dict) and "error" in result:
        return result
    extracted = {}
    for item in result:
        entity_type = item.get("entity_group") or item.get("entity")
        word = item.get("word")
        if entity_type not in extracted:
            extracted[entity_type] = []
        extracted[entity_type].append(word)
    return extracted

## Why

To provide a structured, hands-on learning experience for integrating Hugging Face Inference Providers with a Streamlit frontend. This project explores how to leverage various NLP tasks (Text Classification, Zero-Shot, and Token Classification) while navigating the practical constraints of the Hugging Face free tier.

## What Changes

- **New Learning Resource**: A comprehensive Jupyter Notebook documenting the entire integration, configuration, and deployment process.
- **New Demo Application**: A polished Streamlit application named "MyTravelHelper" that demonstrates real-world use cases for the explored NLP tasks.
- **New Infrastructure**: Integration with Hugging Face Inference Providers and deployment on Hugging Face Spaces.

## Capabilities

### New Capabilities

- `sentiment-analysis`: Analyzing user reviews to determine sentiment (Text Classification).
- `travel-intention`: Classifying user queries into specific travel intentions (Zero-Shot Classification).
- `object-extraction`: Extracting key entities like locations, dates, and organizations from text (Token Classification).
- `topic-detection`: Identifying key themes and topics within user reviews (Zero-Shot/Text Classification).

### Modified Capabilities

<!-- No existing capabilities are being modified. -->

## Impact

- **New Project Files**: `app.py`, `requirements.txt`, and `learning_journey.ipynb`.
- **New Dependencies**: `streamlit`, `huggingface_hub`, `python-dotenv`, `pandas`, and `plotly`.
- **New Infrastructure**: Hugging Face Inference Endpoints and Hugging Face Spaces.

# Project Report: MyTravelHelper AI Integration

## Executive Summary
This report details the development of **MyTravelHelper**, an application designed to automate the analysis of traveler experiences and assist in trip planning using Hugging Face Inference Providers. The project serves as a technical demonstration of integrating serverless NLP models into a Streamlit frontend while operating within the constraints of a free-tier cloud environment.

## 1. Goals and Requirements

### 1.1 Project Goals
The primary objective is to build a lightweight, scalable AI assistant that can extract actionable insights from unstructured travel data. The project aims to demonstrate the efficacy of Zero-Shot and Token Classification for domain-specific tasks without the need for custom model training.

### 1.2 Application Requirements
The application must satisfy the following core functional requirements:
1. **Sentiment Analysis**: Automatically analyze user reviews to determine the overall experience (e.g., Good, Satisfied, Bad, Disappointed).
2. **Travel Intention & Object Extraction**:
   - Analyze user-supplied data to determine travel intention (e.g., Leisure, Business).
   - Perform "Object Extraction" (Named Entity Recognition) to identify locations, dates, and organizations.
3. **Topic Detection**: Identify the specific themes mentioned in user reviews (e.g., food, service, price) to enable granular feedback analysis.

## 2. Overall Architecture

### 2.1 System Architecture
The system follows a decoupled Client-Server architecture. The frontend is hosted as a Streamlit application, which communicates via HTTPS with Hugging Face's serverless Inference API.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                                  │
│  - Inputs: Reviews, Travel Queries, Preferences                         │
│  - Outputs: Sentiment Analytics, Extracted Entities, Detected Topics    │
└────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                     │ (HTTPS / WebSockets)
                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     STREAMLIT FRONTEND (HF Spaces)                      │
│  - Renders UI Components (text inputs, charts, tables)                  │
│  - Manages Session State & User Inputs                                  │
│  - Orchestrates API calls to Hugging Face Inference Providers           │
└────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                     │ (HTTPS POST / JSON)
                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                 HUGGING FACE INFERENCE PROVIDERS (Backend)              │
│  - Routes requests to optimal providers (e.g., hf-inference, Together)  │
│  - Performs model inference on shared/dedicated GPU clusters            │
│  - Returns structured JSON responses                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow
1. **User Input**: The user provides text via the Streamlit interface.
2. **Request Orchestration**: The app uses the `InferenceClient` to send a POST request to the HF API.
3. **Serverless Inference**: HF routes the request to a hosted model (e.g., BART or BERT).
4. **JSON Response**: The API returns a structured list of labels and confidence scores.
5. **Visualization**: Streamlit parses the JSON and renders the result (e.g., a Plotly pie chart for sentiment).

## 3. Configuration Process

### 3.1 Authentication
Access is managed via **User Access Tokens**. These tokens are passed as Bearer tokens in the HTTP Authorization header. For this project, tokens are stored as environment variables (`HF_TOKEN`) to ensure security and portability.

### 3.2 Free Tier Constraints & Management
Operating within the Hugging Face free tier requires specific strategies to maintain stability:
- **Rate Limits**: Limits are enforced per IP address (approx. 1,000 requests per 5-minute window for free users).
- **The Queueing Phenomenon**: Unlike paid tiers, free requests may be queued during peak traffic, leading to silent delays of 30-120 seconds rather than explicit 429 errors.
- **Mitigation**: The implementation utilizes **Exponential Backoff with Jitter** and **Streamlit Caching** (`@st.cache_data`) to reduce redundant API calls.

### 3.3 Error Handling Matrix
| Code | Meaning | Root Cause | Resolution |
| :--- | :--- | :--- | :--- |
| **401** | Unauthorized | Invalid token | Refresh `HF_TOKEN` |
| **403** | Forbidden | Gated model / Permissions | Request model access on Hub |
| **404** | Not Found | Invalid model ID | Verify model ID on Hub |
| **429** | Too Many Requests | Rate limit exceeded | Implement backoff / Upgrade to PRO |
| **503** | Service Unavailable | Model loading / Queueing | Wait for model to initialize |

## 4. Model Selection

Each requirement was mapped to a specific Hugging Face task and model based on accuracy and latency trade-offs:

| Requirement | HF Task | Model Selected | Rationale |
| :--- | :--- | :--- | :--- |
| **Sentiment** | Text Classification | `cardiffnlp/twitter-roberta-base-sentiment-latest` | Three-class model (positive/negative/neutral) better suited for review analysis. |
| **Intention/Topics** | Zero-Shot Classification | `facebook/bart-large-mnli` | Allows custom labels without retraining; high generalization. |
| **Extraction** | Token Classification | `dbmdz/bert-large-cased-finetuned-conll03-english` | Standard for NER; excellent at identifying locations and organizations. |

## 5. Environment Setup and Testing

### 5.1 Setup Workflow
The project utilizes `uv` for high-performance dependency management:
1. **Environment**: Created via `uv venv`.
2. **Dependencies**: Installed using `uv pip install` (Streamlit, huggingface_hub, pandas, plotly).
3. **Configuration**: `.env` file configured for local development.

### 5.2 Verification Strategy
A dedicated test suite (`tests/test_app.py`) was implemented to validate the core NLP helpers independently of the UI. All four core functions passed verification.

## 6. Running the App & QA

### 6.1 Execution
The app is launched via `streamlit run app/app.py`. It is designed for deployment on **Hugging Face Spaces**, where `HF_TOKEN` is configured as a Repository Secret.

### 6.2 QA Testing Results
- **Scenario A (Positive Review)**: Correctly identified as POSITIVE sentiment with >90% confidence.
- **Scenario B (Ambiguous Query)**: Zero-shot classification correctly mapped a "romantic getaway" query to "leisure vacation".
- **Scenario C (NER Extraction)**: Correctly extracted "Paris" (LOC) and "British Airways" (ORG) from travel plans.

### 6.3 Extensible Functionalities
The architecture allows for easy expansion by adding new candidate labels to the Zero-Shot classifier or replacing the underlying models in `app/utils.py` without changing the frontend code.

## 7. Customer Satisfaction Analytics

This module uses **Text Classification** to process user reviews. By analyzing the dominant sentiment and visualizing the distribution using a Plotly pie chart, the system can provide an aggregate "health score" of customer satisfaction.

**Implementation Detail**: The app handles batch processing of reviews by iterating through a list and aggregating the results into a Pandas DataFrame before visualization.

## 8. Detecting Topics mentioned from the Review

This module leverages **Zero-Shot Classification** to detect themes like "cleanliness" or "pricing". Unlike standard classification, this approach allows the business to change the monitored topics instantly without needing to retrain the model.

**Key Metric**: Only topics with a confidence score above 0.5 are displayed to the user to reduce false positives.

import os
import unittest
from unittest.mock import patch, MagicMock
from app.utils import (
    analyze_sentiment,
    detect_topics,
    analyze_travel_intent,
    extract_travel_objects,
    _call_with_retry,
    _get_error_message,
    _should_retry,
    ERROR_MESSAGES,
)
from huggingface_hub import InferenceTimeoutError
from huggingface_hub.errors import HfHubHTTPError
from dotenv import load_dotenv

load_dotenv()


class TestErrorHelpers(unittest.TestCase):
    def test_error_messages_defined(self):
        for code in [401, 403, 404, 429, 503]:
            self.assertIn(code, ERROR_MESSAGES)
            self.assertIsInstance(ERROR_MESSAGES[code], str)

    def test_get_error_message_known(self):
        self.assertIn("HF_TOKEN", _get_error_message(401))

    def test_get_error_message_unknown(self):
        msg = _get_error_message(500)
        self.assertIn("500", msg)

    def test_should_retry_true(self):
        self.assertTrue(_should_retry(429))
        self.assertTrue(_should_retry(503))

    def test_should_retry_false(self):
        self.assertFalse(_should_retry(401))
        self.assertFalse(_should_retry(403))
        self.assertFalse(_should_retry(404))
        self.assertFalse(_should_retry(400))
        self.assertFalse(_should_retry(500))


class TestCallWithRetry(unittest.TestCase):
    def test_success_first_attempt(self):
        func = MagicMock(return_value="ok")
        result = _call_with_retry(func)
        self.assertEqual(result, "ok")
        func.assert_called_once()

    def test_non_retryable_error(self):
        func = MagicMock()
        response = MagicMock()
        response.status_code = 401
        func.side_effect = HfHubHTTPError("Unauthorized", response=response)
        result = _call_with_retry(func, max_retries=3)
        self.assertIn("error", result)
        self.assertIn("HF_TOKEN", result["error"])
        func.assert_called_once()

    def test_retryable_then_success(self):
        func = MagicMock()
        success_response = MagicMock()
        success_response.status_code = 200
        error_response = MagicMock()
        error_response.status_code = 503
        func.side_effect = [
            HfHubHTTPError("Service Unavailable", response=error_response),
            HfHubHTTPError("Service Unavailable", response=error_response),
            "ok",
        ]
        with patch("app.utils.time.sleep"):
            result = _call_with_retry(func, max_retries=5, base_delay=0.01)
        self.assertEqual(result, "ok")
        self.assertEqual(func.call_count, 3)

    def test_retryable_exhausted(self):
        func = MagicMock()
        response = MagicMock()
        response.status_code = 429
        func.side_effect = HfHubHTTPError("Too Many Requests", response=response)
        with patch("app.utils.time.sleep"):
            result = _call_with_retry(func, max_retries=3, base_delay=0.01)
        self.assertIn("error", result)
        self.assertIn("Rate limit", result["error"])
        self.assertEqual(func.call_count, 3)

    def test_timeout_retry_then_success(self):
        func = MagicMock()
        func.side_effect = [
            InferenceTimeoutError("Timeout"),
            InferenceTimeoutError("Timeout"),
            "ok",
        ]
        with patch("app.utils.time.sleep"):
            result = _call_with_retry(func, max_retries=5, base_delay=0.01)
        self.assertEqual(result, "ok")
        self.assertEqual(func.call_count, 3)

    def test_timeout_exhausted(self):
        func = MagicMock()
        func.side_effect = InferenceTimeoutError("Timeout")
        with patch("app.utils.time.sleep"):
            result = _call_with_retry(func, max_retries=2, base_delay=0.01)
        self.assertIn("error", result)
        self.assertIn("timed out", result["error"])
        self.assertEqual(func.call_count, 2)

    def test_generic_exception(self):
        func = MagicMock(side_effect=ValueError("weird error"))
        result = _call_with_retry(func)
        self.assertIn("error", result)
        self.assertIn("weird error", result["error"])


class TestNLPHelpersWithMocks(unittest.TestCase):
    @patch("app.utils.client.text_classification")
    def test_analyze_sentiment_error_dict(self, mock_tc):
        response = MagicMock()
        response.status_code = 401
        mock_tc.side_effect = HfHubHTTPError("Unauthorized", response=response)
        result = analyze_sentiment("test")
        self.assertIn("error", result)
        self.assertIn("HF_TOKEN", result["error"])

    @patch("app.utils.client.zero_shot_classification")
    def test_detect_topics_error(self, mock_zsc):
        response = MagicMock()
        response.status_code = 503
        mock_zsc.side_effect = HfHubHTTPError("Unavailable", response=response)
        with patch("app.utils.time.sleep"):
            result = detect_topics("test", ["a"])
        self.assertIn("error", result)

    @patch("app.utils.client.zero_shot_classification")
    def test_analyze_travel_intent_error(self, mock_zsc):
        response = MagicMock()
        response.status_code = 500
        mock_zsc.side_effect = HfHubHTTPError("Server Error", response=response)
        result = analyze_travel_intent("test")
        self.assertTrue(result.startswith("Error:"))

    @patch("app.utils.client.token_classification")
    def test_extract_travel_objects_error(self, mock_tc):
        response = MagicMock()
        response.status_code = 404
        mock_tc.side_effect = HfHubHTTPError("Not Found", response=response)
        result = extract_travel_objects("test")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()

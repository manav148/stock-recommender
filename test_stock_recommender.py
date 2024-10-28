import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from stock_utils import get_stock_price, google_query, get_recent_stock_news, get_financial_statements
from llm_utils import get_llm, create_chat_openai, create_bedrock_chat
from ui_utils import setup_sidebar

class TestStockRecommender(unittest.TestCase):

    @patch('yfinance.Ticker')
    def test_get_stock_price(self, mock_ticker):
        mock_history = pd.DataFrame({
            'Close': [100, 101, 102],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_ticker.return_value.history.return_value = mock_history

        result = get_stock_price("AAPL")
        self.assertIn("Date", result)
        self.assertIn("Close", result)
        self.assertIn("Volume", result)

    def test_google_query(self):
        result = google_query("Apple")
        self.assertEqual(result, "https://www.google.com/search?q=Apple+stock+news")

    @patch('requests.get')
    def test_get_recent_stock_news(self, mock_get):
        mock_get.return_value.text = "<html><div class='n0jPhd ynAwRc tNxQIb nDgy9d'>Mocked news</div></html>"
        result = get_recent_stock_news("Apple")
        self.assertIn("Mocked news", result)

    @patch('yfinance.Ticker')
    def test_get_financial_statements(self, mock_ticker):
        mock_balance_sheet = pd.DataFrame({
            '2023-12-31': [100, 200, 300],
            '2022-12-31': [90, 180, 270],
            '2021-12-31': [80, 160, 240]
        }, index=['Assets', 'Liabilities', 'Equity'])
        
        mock_ticker.return_value.balance_sheet = mock_balance_sheet

        result = get_financial_statements("AAPL")
        self.assertIn("Assets", result)
        self.assertIn("Liabilities", result)
        self.assertIn("Equity", result)

    @patch('llm_utils.create_chat_openai')
    def test_get_llm_openai(self, mock_create_chat_openai):
        mock_instance = MagicMock()
        mock_create_chat_openai.return_value = mock_instance
        result = get_llm("OpenAI", {"openai_api_key": "test_key"})
        self.assertEqual(result, mock_instance)
        mock_create_chat_openai.assert_called_once_with({"openai_api_key": "test_key"})

    @patch('llm_utils.create_bedrock_chat')
    def test_get_llm_bedrock(self, mock_create_bedrock_chat):
        mock_instance = MagicMock()
        mock_create_bedrock_chat.return_value = mock_instance
        result = get_llm("Bedrock", {
            "use_aws_profile": True,
            "aws_profile": "ziya",
            "aws_region": "us-east-1",
            "bedrock_model": "test_model"
        })
        self.assertEqual(result, mock_instance)
        mock_create_bedrock_chat.assert_called_once_with({
            "use_aws_profile": True,
            "aws_profile": "ziya",
            "aws_region": "us-east-1",
            "bedrock_model": "test_model"
        })

    @patch('streamlit.sidebar')
    def test_setup_sidebar(self, mock_sidebar):
        mock_sidebar.radio.return_value = "OpenAI"
        mock_sidebar.text_input.return_value = "test_key"
        
        llm_option, llm_params = setup_sidebar()
        self.assertEqual(llm_option, "OpenAI")
        self.assertEqual(llm_params["openai_api_key"], "test_key")

if __name__ == '__main__':
    unittest.main()
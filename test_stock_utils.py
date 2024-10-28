import pytest
from stock_utils import get_stock_price, google_query, get_recent_stock_news, get_financial_statements

@pytest.mark.stock
def test_get_stock_price():
    """Test the get_stock_price function with a real stock ticker."""
    result = get_stock_price('GOOG')
    assert isinstance(result, str)
    assert 'Date' in result
    assert 'Close' in result
    assert 'Volume' in result

@pytest.mark.query
def test_google_query():
    """Test the google_query function with different inputs."""
    result = google_query('Apple')
    assert result == 'https://www.google.com/search?q=Apple+stock+news'

    result = google_query('Tesla news')
    assert result == 'https://www.google.com/search?q=Tesla+news'

@pytest.mark.news
def test_get_recent_stock_news():
    """Test the get_recent_stock_news function with a real company name."""
    result = get_recent_stock_news('Apple')
    assert isinstance(result, str)
    assert 'Recent News:' in result
    assert len(result.split('\n')) > 2  # Ensure we have at least one news item

@pytest.mark.financial
def test_get_financial_statements():
    """Test the get_financial_statements function with a real stock ticker."""
    result = get_financial_statements('AAPL')
    assert isinstance(result, str)
    assert 'Cash' in result or 'Assets' in result or 'Liabilities' in result

if __name__ == '__main__':
    pytest.main([__file__])
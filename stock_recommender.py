import streamlit as st
from langchain.agents import Tool, initialize_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.callbacks.base import BaseCallbackHandler
import time

from stock_utils import get_stock_price, get_recent_stock_news, get_financial_statements
from llm_utils import get_llm
from ui_utils import set_background, setup_sidebar
from email_utils import generate_email_content, send_email

class RealTimeCallback(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.step_containers = {}

    def on_tool_start(self, serialized, input_str, **kwargs):
        step_container = self.container.expander(f"Step: {serialized['name']}")
        self.step_containers[serialized['name']] = step_container
        with step_container:
            st.write(f"**Input:** {input_str}")

    def on_tool_end(self, output, **kwargs):
        current_step = list(self.step_containers.keys())[-1]
        with self.step_containers[current_step]:
            st.write(f"**Output:** {output}")

def analyze_stock(zero_shot_agent, stock, container):
    prompt = f'Is {stock} a good investment choice right now?'
    callback = RealTimeCallback(container)
    response = zero_shot_agent(prompt, callbacks=[callback])
    return response

def main():
    set_background('bcg_light.png')
    st.header('Stock Recommendation System')

    llm_option, llm_params = setup_sidebar()
    llm = get_llm(llm_option, llm_params)

    if llm:
        tools = [
            Tool(
                name="Stock Ticker Search",
                func=DuckDuckGoSearchRun().run,
                description="Use only when you need to get stock ticker from internet, you can also get recent stock related news. Don't use it for any other analysis or task"
            ),
            Tool(
                name="Get Stock Historical Price",
                func=get_stock_price,
                description="Use when you are asked to evaluate or analyze a stock. This will output historic share price data. You should input the stock ticker to it"
            ),
            Tool(
                name="Get Recent News",
                func=get_recent_stock_news,
                description="Use this to fetch recent news about stocks"
            ),
            Tool(
                name="Get Financial Statements",
                func=get_financial_statements,
                description="Use this to get financial statement of the company. With the help of this data company's historic performance can be evaluated. You should input stock ticker to it"
            )
        ]

        zero_shot_agent = initialize_agent(
            llm=llm,
            agent="zero-shot-react-description",
            tools=tools,
            verbose=True,
            max_iteration=4,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )

        stock_prompt = """You are a financial advisor. Give stock recommendations for given query.
        Everytime first you should identify the company name and get the stock ticker symbol for the stock.
        Answer the following questions as best you can. You have access to the following tools:

        Get Stock Historical Price: Use when you are asked to evaluate or analyze a stock. This will output historic share price data. You should input the stock ticker to it 
        Stock Ticker Search: Use only when you need to get stock ticker from internet, you can also get recent stock related news. Don't use it for any other analysis or task
        Get Recent News: Use this to fetch recent news about stocks
        Get Financial Statements: Use this to get financial statement of the company. With the help of this data company's historic performance can be evaluated. You should input stock ticker to it

        steps- 
        Note- if you fail in satisfying any of the step below, Just move to next one
        1) Get the company name and search for the "company name + stock ticker" on internet. Don't hallucinate extract stock ticker as it is from the text. Output- stock ticker. If stock ticker is not found, stop the process and output this text: This stock does not exist
        2) Use "Get Stock Historical Price" tool to gather stock info. Output- Stock data
        3) Get company's historic financial data using "Get Financial Statements". Output- Financial statement
        4) Use this "Get Recent News" tool to search for latest stock related news. Output- Stock news
        5) Analyze the stock based on gathered data and give detailed analysis for investment choice. provide numbers and reasons to justify your answer. Output- Give a single answer if the user should buy,hold or sell. You should Start the answer with Either Buy, Hold, or Sell in Bold after that Justify.

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do, Also try to follow steps mentioned above
        Action: the action to take, should be one of [Get Stock Historical Price, Stock Ticker Search, Get Recent News, Get Financial Statements]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times, if Thought is empty go to the next Thought and skip Action/Action Input and Observation)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        Begin!

        Question: {input}
        Thought:{agent_scratchpad}"""

        zero_shot_agent.agent.llm_chain.prompt.template = stock_prompt

        stocks = st.text_area("Enter stock symbols (comma-separated):", "AAPL, GOOGL, MSFT")
        email = st.text_input("Enter your email address (optional):")
        
        if st.button("Analyze Stocks"):
            stock_list = [s.strip() for s in stocks.split(',')]
            results = {}

            for stock in stock_list:
                st.write(f"**Analysis for {stock}**")
                stock_container = st.container()
                with st.spinner(f'Analyzing {stock}...'):
                    response = analyze_stock(zero_shot_agent, stock, stock_container)
                    results[stock] = response["output"]
                    
                    st.write("**Final Recommendation:**")
                    st.write(response["output"])
                    st.write("---")
                time.sleep(5)  # Add a 5-second delay between stocks to prevent throttling

            if email:
                email_content = generate_email_content(results)
                success, message = send_email(email, "Stock Recommendations", email_content)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        st.warning("Please provide the necessary API key or AWS credentials to proceed.")

if __name__ == "__main__":
    main()

import streamlit as st
import base64

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def setup_sidebar():
    llm_option = st.sidebar.radio("Select LLM Provider", ("Bedrock", "OpenAI"))
    llm_params = {}

    if llm_option == "Bedrock":
        llm_params['aws_region'] = st.sidebar.text_input('AWS Region', value='us-east-1')
        llm_params['use_aws_profile'] = st.sidebar.checkbox('Use AWS Profile')
        if llm_params['use_aws_profile']:
            llm_params['aws_profile'] = st.sidebar.text_input('AWS Profile Name', value='ziya')
        else:
            llm_params['aws_access_key'] = st.sidebar.text_input('AWS Access Key ID', type='password')
            llm_params['aws_secret_key'] = st.sidebar.text_input('AWS Secret Access Key', type='password')
        
        llm_params['bedrock_model'] = st.sidebar.selectbox(
            "Select Bedrock Model",
            ("anthropic.claude-3-5-sonnet-20240620-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0", ),
            index=0
        )
    else:
        llm_params['openai_api_key'] = st.sidebar.text_input('OpenAI API Key', type='password')

    st.sidebar.write('This tool provides recommendation based on the RAG & ReAct Based Schemes:')
    lst = ['Get Ticker Value', 'Fetch Historic Data on Stock', 'Get Financial Statements', 'Scrape the Web for Stock News', 'LLM ReAct based Verbal Analysis', 'Output Recommendation: Buy, Sell, or Hold with Justification']

    s = ''
    for i in lst:
        s += "- " + i + "\n"
    st.sidebar.markdown(s)

    return llm_option, llm_params
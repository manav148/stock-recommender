import boto3
from langchain_community.chat_models import ChatOpenAI, BedrockChat

def create_chat_openai(params):
    return ChatOpenAI(temperature=0, model_name='gpt-4-turbo', openai_api_key=params['openai_api_key'])

def create_bedrock_chat(params):
    if params['use_aws_profile']:
        session = boto3.Session(profile_name=params['aws_profile'], region_name=params['aws_region'])
    else:
        session = boto3.Session(
            aws_access_key_id=params['aws_access_key'],
            aws_secret_access_key=params['aws_secret_key'],
            region_name=params['aws_region']
        )
    
    bedrock_client = session.client('bedrock-runtime')
    return BedrockChat(
        model_id=params['bedrock_model'],
        client=bedrock_client,
        model_kwargs={"temperature": 0}
    )

def get_llm(llm_option, params):
    if llm_option == "OpenAI":
        return create_chat_openai(params)
    else:
        # Default to Bedrock for any other option, including "Bedrock" or invalid inputs
        return create_bedrock_chat(params)
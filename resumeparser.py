# Import libraries
from groq import Groq  # Replace OpenAI with Groq
import yaml
import json
import re

api_key = None
CONFIG_PATH = r"config.yaml"

# Load API key from config.yaml
with open(CONFIG_PATH) as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    api_key = data['GROQ_API_KEY']  # Update to use GROQ_API_KEY

def ats_extractor(resume_data):
    prompt = '''
    You are an AI bot that extracts structured data from resumes.  
    Extract the following fields in **valid JSON format**:  

    - fullname  
    - emailid  
    - githubportfolio  
    - linkedinid  
    - employmentdetails (as an array)  
    - skills (combine technical and soft skills into a single array)  

    **Return ONLY valid JSON output without any additional text or explanation.**  
    '''

    # Initialize Groq client
    groq_client = Groq(api_key=api_key)

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": resume_data}
    ]

    # Make API call to Groq
    response = groq_client.chat.completions.create(
        model="gemma2-9b-it",  # Replace with the correct model
        messages=messages,
        temperature=0.0,
        max_tokens=1500
    )

    # Extract the response content
    data = response.choices[0].message.content.strip()
    match = re.search(r"\{.*\}", data, re.DOTALL)  # Find JSON object
    if match:
        print(match)
        try:
            print(json.loads(match.group(0)))
            return json.loads(match.group(0))  # Convert JSON string to dictionary
        except json.JSONDecodeError:
            print("Invalid JSON format received.")
            return None
    return None



from groq import Groq

def getcheck(desc, resume_data):
    """
    Compares a job description with a resume and returns a match percentage.

    :param desc: Job description as a string.
    :param resume_data: Resume content as a string.
    :return: Match percentage as a JSON object.
    """
    
    # Define the prompt
    prompt = """
  Compare the given job description and resume. 
    Provide only the match percentage in strict JSON format as { "percent": value }.
    Do not include any explanation, reasoning, or additional text.
    """
  

    # Initialize Groq client (Make sure api_key is correctly set)
    groq_client = Groq(api_key=api_key)  # Replace with your actual API key

    # Format messages properly
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Job Description: {desc}\nResume: {resume_data}"}
    ]

    # Call Groq API for chat completion
    response = groq_client.chat.completions.create(
        model="gemma2-9b-it",  # Ensure this model is correct
        messages=messages,
        temperature=0.0,
        max_tokens=150
    )

    # Extract and return the response content
    data = response.choices[0].message.content.strip()
    match = re.search(r"\{.*\}", data, re.DOTALL)
    print(match)

    if match:
        print(match)
        try:
            print(json.loads(match.group(0)))
            return json.loads(match.group(0))  # Convert JSON string to dictionary
        except json.JSONDecodeError:
            print("Invalid JSON format received.")
            return None
    return None

     # This should be a JSON string like '{ "percent": 85 }'

# # Example usage
# desc = "Looking for a Python Developer with experience in Flask and PostgreSQL."
# resume_data = "I have worked with Flask, Django, and PostgreSQL in my previous roles."
# match_result = getcheck(desc, resume_data)
# print("match result")
# print(match_result.get("percent"))


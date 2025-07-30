import pandas as pd
from secret_keys import openaikey
from openai import OpenAI
import tiktoken
from model import model_columns
from io import StringIO
import os

def main():
    key = openaikey
    
    global client
    client = OpenAI(api_key=key)
    
    biographical_info = load_biographies()
    body = load_prompt()
    model_string = load_model_string(model_columns)

    all_dataframes = []

    # Create the generated_frames folder if it doesn't exist
    output_folder = 'generated_frames'
    os.makedirs(output_folder, exist_ok=True)
    
    for i, bio in enumerate(biographical_info):
      print(f"Processing biography {i+1}/{len(biographical_info)}: {bio['Name']}")
        
      prompt = construct_prompt(body, bio["Name"], bio["Biography"], model_string)
      df = generate_table(prompt)
        
      # Validate the result
      if df.empty:
        print(f"  Warning: No data extracted for {bio['Name']}")
      elif not all(col in model_columns for col in df.columns):
        # Find the columns that caused the failure
        invalid_columns = [col for col in df.columns if col not in model_columns]
        print(f"  Warning: Column validation failed for {bio['Name']}")
        print(f"    Invalid columns found: {invalid_columns}")
        print(f"    Expected columns: {model_columns}")
      else:
        print(f"  Success: {len(df)} rows extracted")
        
        df['URI'] = f"person_{i}"
        df['name'] = bio['Name']
        df['source_name'] = bio["Source"]
        df['source_page'] = bio['SourcePage']
        all_dataframes.append(df)

        #save individual frames to folder
        safe_name = "".join(c for c in bio['Name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}_{i+1}.csv"
        filepath = os.path.join(output_folder, filename)

        df.to_csv(filepath, encoding='UTF-8', index=False)
        print(f" Saved to: {filepath}")

    return all_dataframes

def clean_csv_response(response):
    """Clean AI response to extract just the CSV content"""
    lines = response.strip().split('\n')
    csv_lines = []
    
    for line in lines:
        # Skip markdown code block markers and empty lines
        if line.strip() in ['```csv', '```', ''] or line.strip().startswith('```'):
            continue
        # Keep lines that look like CSV (contain commas or quotes)
        if ',' in line or line.startswith('"'):
            csv_lines.append(line)
    
    return '\n'.join(csv_lines)

def generate_table(prompt):
    answer = askgpt(prompt)

    clean_answer = clean_csv_response(answer)

    df = pd.read_csv(StringIO(clean_answer))

    return df
    
def construct_prompt(body, name, biography, model_string):    
    prompt = f"""
    I will provide a biographical text of {name}. 
    
    Please return their biographical details as a csv-formatted table using these columns: {model_string}.
    
    Do not include information that does not fit in this schema. Only return the CSV.

    {body}

    biography:
    {biography}
    """

    return prompt

def load_model_string(model):
    output = "["
    for column_name in model:
        output = output + str(column_name) + ", "

    output = output + "]"

    return output

def load_prompt():
    with open("prompt.txt") as f:
        return f.read()

def load_biographies():
    df = pd.read_csv("samples/input.csv", encoding='UTF-8')
    output = df.to_dict(orient='records')        
    return output

# Tokenizer helper function
# gpt-4o uses o200k_base, gpt-4-turbo and older use the cl100k_base
def checktokens(labels, tokmodel="o200k_base", bias=100, verbose=True):
    en = tiktoken.get_encoding(tokmodel)
    toklist = pd.DataFrame(columns=['labels', 'tokens', 'length'])
    toklist['labels'] = labels
    toklist['tokens'] = None
    toklist['length'] = None
    for i, label in enumerate(labels):
        tks = en.encode(label)
        toklist.at[i, 'tokens'] = ' '.join(map(str, tks))
        toklist.at[i, 'length'] = len(tks)
    if verbose:
      print(toklist)
    logit_bias = {token: bias for token in set(toklist['tokens'].str.split(' ', expand=True).stack())}
    return logit_bias

# Function to call OpenAI API; requires key to be set above
def askgpt(input, max_tokens=None, logit_bias=None, model= "gpt-4o"):
  response = client.chat.completions.create(
    model= model,
    messages = [{"role": "user", "content": input }],
    max_tokens = max_tokens,
    temperature = 0.7,
    logit_bias = logit_bias
  )
  return response.choices[0].message.content

if __name__ == "__main__":
    main()
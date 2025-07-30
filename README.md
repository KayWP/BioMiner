# BioMiner
BioMiner is a Python application that extracts historical data from biographical texts using a LLM, then provides a Streamlit-based workflow for reviewing and editing the results.

### Prerequisites

- Python 3.7+
- OpenAI API key (or other LLM-key)
- Required Python packages (pandas, openai, tiktoken, streamlit)

### Set up
1. Set up your OpenAI API key:
   - Create a `secret_keys.py` file
   - Add your API key: `openaikey = "your-api-key-here"`

2. Configure your data model:
   - Edit `model.py` to define your desired column structure. The script will provide this to the model, and check the output against it.
   - Update `prompt.txt` with specific extraction instructions, ideally explaining the columns provided in `model.py`

### Usage

#### Step 1: Prepare Your Data
Create a CSV file at `samples/input.csv` with columns:
- `Name`: Person's name
- `Biography`: Biographical text
- `Source`: Source reference
- `SourcePage`: Page number or reference

#### Step 2: Extract Biographical Data
```bash
python aiProcessing.py
```
This will:
- Process each biography through the AI model
- Extract structured data according to your schema
- Save individual CSV files in `generated_frames/`
- Validate results and report any issues

#### Step 3: Review and Refine
```bash
streamlit run streamlitApp.py
```
The interactive review interface allows you to:
- Navigate through extracted records
- Edit data directly in the browser
- Track completion progress
- Export final results to `output.csv`

## 📁 Project Structure
Make sure your project is structured like this.
```
biominer/
├── aiProcessing.py      # Main extraction script
├── streamlitApp.py      # Interactive review interface
├── model.py             # Data model definition
├── prompt.txt           # AI extraction instructions
├── secret_keys.py       # API keys (create this)
├── samples/
│   └── input.csv        # Input biographical data
├── generated_frames/    # Individual extracted CSV files
└── output.csv          # Final reviewed dataset
```

## ⚙️ Configuration

### Data Model (`model.py`)
Define the columns you want to extract. For example:
```python
model_columns = [
    "birth_date",
    "birth_place", 
    "occupation",
    "education",
    # Add your desired fields
]
```

### Extraction Prompt (`prompt.txt`)
Customize the AI instructions for better extraction accuracy. Include:
- Specific formatting requirements
- Explanation of the columns
- Examples of desired output

### Processing Parameters
Modify `aiProcessing.py` to adjust:
- OpenAI model selection (`gpt-4o`, `gpt-4-turbo`, etc.)
- Temperature settings for creativity vs. consistency
- Token limits and bias settings

### Data Validation
Automatic validation ensures extracted data matches your schema:
- Column name verification
- Empty result detection
- Invalid data type warnings

### Progress Tracking
The Streamlit interface provides visual progress indicators and completion tracking across all records.

## 📊 Output
BioMiner generates:
- **Individual uncurated CSV files**: One per biography in `generated_frames/`
- **Combined dataset**: Final reviewed data in `output.csv`
- **Processing logs**: Console output with validation results

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **API Costs**: This tool uses OpenAI's API which incurs costs. Monitor your usage!
- **Data Privacy**: Ensure biographical data complies with privacy regulations
- **API Keys**: Never commit your `secret_keys.py` file to version control

import pdfplumber
import pandas as pd

# Path to the uploaded PDF
pdf_path = "./MIDSEM.pdf"

# Extract text from the PDF
data = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        tables = page.extract_table()
        if tables:
            data.extend(tables)

# Convert to DataFrame
df = pd.DataFrame(data)
print(df.head())  # Show first few rows to inspect data structure

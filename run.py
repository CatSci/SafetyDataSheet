import streamlit as st
import pandas as pd
import re
import pdfplumber

hcode_statement_file = 'hazard_code.xlsx'

def read_hcode_pdf(file):
    h_statement = []
    with pdfplumber.open(file) as pdf:
        total_pages = len(pdf.pages)
        for i in range(0, total_pages): 
            page = pdf.pages[i]
            text = page.extract_text()

            for line in text.split('\n'):
                a = re.findall(r'H[0-9][0-9][0-9][A-Z]', line)
                c = re.findall(r'H[0-9][0-9][0-9].', line)
                if a:
                    h_statement.append(a)
                if c:
                    h_statement.append(c)
    
    return h_statement


def clean_hcode(h_statement):
    clean_code = []
    check_char_caps = re.compile('H[0-9][0-9][0-9][A-Z]')
    check_char_small = re.compile('H[0-9][0-9][0-9][a-z]')
    for i in range(len(h_statement)):
        if len(h_statement[i]) > 1:
            for j in range(len(h_statement[i])):
                temp = h_statement[i][j]
                if check_char_caps.fullmatch(temp) or check_char_small.fullmatch(temp):
                    clean_code.append(temp)
                else:
                    clean_code.append(temp[:-1])
        else:
            temp = h_statement[i][0]
            if check_char_caps.fullmatch(temp) or check_char_small.fullmatch(temp):
                clean_code.append(temp)
            else:
                clean_code.append(temp[:-1])

    return clean_code


def hcode_statement(clean_code, hcode_statement_file):
    unique_code = list(set(clean_code))
    health_hazard = {}
    sheets = ['Physical Hazards', 'Health Hazards', 'Environmental Hazards']
    for sn in sheets:
        df = pd.read_excel(hcode_statement_file, sheet_name = sn)
        for val in unique_code:
            result = df.isin([val]).any().any()
            if result:
                idx = df[df['code'] == val].index
                c = df.iloc[idx[0], 0]
                s = df.iloc[idx[0], 1]
                health_hazard[c] = s

    return health_hazard


def get_statement(health_hazard):
    new_df = pd.DataFrame.from_dict(health_hazard, orient = 'index')
    new_df.reset_index(inplace = True)
    new_df.rename(columns = {'index': 'Code', 0: 'Hazard Statements'}, inplace = True)
    
    return new_df



def main(pdf_file):
    h_statement = read_hcode_pdf(pdf_file)
    clean_code = clean_hcode(h_statement)
    health_hazard = hcode_statement(clean_code, hcode_statement_file)
    df = get_statement(health_hazard)
    return df


# if __name__ == "__main__":
#     df = main()
#     print(df)
st.title('Hazard Statements')

uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

if uploaded_file is not None:
    df = main(uploaded_file)
    st.write(df)

    st.download_button(
    label= 'Download Data',
    data = df.to_csv().encode('utf-8'),
    file_name = 'Hazard_Statement.csv',
    mime= 'text/csv'
    )



# Hoveyda-Grubbs Catalyst - Sigma.pdf (exception no h code)

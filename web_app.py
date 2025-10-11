import streamlit as st
import pandas as pd
import os
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Product Details Viewer",
    page_icon="📦",
    layout="wide"
)

# --- Configuration ---
# SET YOUR CSV FILE PATH HERE
CSV_PATH = 'dataset/train.csv'

# --- Local Formatting Function ---
def format_content_locally(text: str) -> str:
    """
    Parses the raw catalog content, formats it into key-value pairs,
    and highlights specific keywords in red.
    """
    # Define the keywords to highlight
    keywords_to_highlight = ['Unit', 'Value', 'Bullet Point', 'Bullet Poin', 'Item Name']
    highlight_template = r'<span style="color:red; font-weight:bold;">\1</span>'

    # This regex finds all potential keys (patterns of words ending with a colon).
    keys = re.findall(r'(\w[\w\s\d]*:)', text)
    
    # If no keys are found, fall back to splitting by sentences and highlighting keywords.
    if not keys:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Create a markdown bulleted list
        bullet_list = "\n".join([f"&bull; {s.strip()}" for s in sentences if s.strip()])
        
        # Process the list to highlight keywords
        processed_list = bullet_list
        for keyword in keywords_to_highlight:
             # Use word boundaries (\b) to match whole words only, case-insensitive
             processed_list = re.sub(r'\b({})\b'.format(re.escape(keyword)), highlight_template, processed_list, flags=re.IGNORECASE)
        return processed_list

    # Create a regex pattern to split the text by all the keys found.
    split_pattern = '|'.join(map(re.escape, keys))
    values = re.split(f'({split_pattern})', text)
    
    formatted_output = []
    # Iterate through the list, pairing keys with their subsequent values.
    for i in range(1, len(values), 2):
        key = values[i].strip()
        value = values[i+1].strip()
        
        # The key itself is bolded.
        bold_key = f"**{key}**"
        
        # Process the value to highlight any matching keywords.
        processed_value = value
        for keyword in keywords_to_highlight:
            processed_value = re.sub(r'\b({})\b'.format(re.escape(keyword)), highlight_template, processed_value, flags=re.IGNORECASE)
        
        formatted_output.append(f"{bold_key} {processed_value}")
        
    # Join the formatted lines with double newlines for spacing.
    return "\n\n".join(formatted_output)

# --- Main Application ---
st.title("📦 Product Details Viewer")
st.markdown("This app displays product details with local content formatting.")

# --- Main Logic ---
if os.path.exists(CSV_PATH):
    try:
        df = pd.read_csv(CSV_PATH)

        required_columns = ['sample_id', 'image_link', 'catalog_content']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: The CSV must contain the columns: {', '.join(required_columns)}")
        else:
            st.sidebar.header("Select a Product")
            sample_ids = df['sample_id'].unique()
            selected_id = st.sidebar.selectbox(
                'Select a Sample ID:',
                options=sample_ids
            )

            if selected_id:
                product_details = df[df['sample_id'] == selected_id].iloc[0]

                st.header(f"Details for Product: {selected_id}", divider='rainbow')

                st.subheader("Product Description")
                raw_description = str(product_details.get('catalog_content', 'No description available.'))

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("##### Formatted Description")
                    with st.container(border=True, height=300):
                        # Use the local formatting function instead of an API call
                        formatted_description = format_content_locally(raw_description)
                        st.markdown(formatted_description, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("##### Raw Content (with Highlighting)")
                    # Removed the fixed height to prevent a scrollbar
                    with st.container(border=True):
                        # Apply the same keyword highlighting to the raw text
                        keywords_to_highlight = ['Unit', 'Value', 'Bullet Point', 'Bullet Poin', 'Item Name']
                        highlight_template = r'<span style="color:red; font-weight:bold;">\1</span>'
                        highlighted_raw_text = raw_description
                        for keyword in keywords_to_highlight:
                             highlighted_raw_text = re.sub(r'\b({})\b'.format(re.escape(keyword)), highlight_template, highlighted_raw_text, flags=re.IGNORECASE)
                        # Use st.markdown to render the HTML tags
                        st.markdown(highlighted_raw_text, unsafe_allow_html=True)

                st.divider()

                img_col, details_col = st.columns([1, 2])

                with img_col:
                    st.subheader("Product Image")
                    image_url = product_details['image_link']
                    st.image(
                        image_url,
                        caption=f"ID: {selected_id}",
                        width=200 # Reduced width for a smaller image
                    )
                
                with details_col:
                    st.subheader("All Product Details")
                    st.table(product_details.transpose())

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.error(f"Error: The file was not found at the specified path: '{CSV_PATH}'")
    st.info(
        f"""
        **Please make sure the CSV file exists at that location.**
        - The current working directory is: `{os.getcwd()}`
        - The script is looking for the file at the absolute path: `{os.path.abspath(CSV_PATH)}`
        """
    )


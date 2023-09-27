import streamlit as st
import json
import html
import re
import codecs


# Read names.json and preprocess the data
with open('names.json', 'r') as names_file:
    names_data = json.load(names_file)
    user_index = {name_info['roll']: name_info for name_info in names_data['names']}
    lowercase_names = {name_info['name'].lower(): name_info for name_info in names_data['names']}

# Function to generate user links with proper routing
def generate_user_link(user_info):
    return f"<a href='/?rollnumber={user_info['roll']}' target='_self' rel='noopener noreferrer'>{user_info['name']} ({user_info['roll']})</a>"

def format_html(input_text):
    def replace_html_entities(match):
        return html.unescape(match.group(0))
    def replace_unicode_escapes(match):
        return chr(int(match.group(1), 16))
    processed_text = re.sub(r'&[a-zA-Z]+;', replace_html_entities, input_text)
    processed_text = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode_escapes, processed_text)
    # Replace emoji encodings (e.g., ðŸ˜ to 😄)
    # processed_text = emoji.emojize(processed_text)
    processed_text = processed_text.replace('\\n', '<br>')
    return processed_text

# Streamlit app
st.title('Testimonial Viewer')

# Page 1: Search for Users (Left part)
st.sidebar.header('Search for User')
search_option = st.sidebar.radio('Select search option:', ['By Name', 'By Roll Number'])

if search_option == 'By Name':
    search_name = st.sidebar.text_input('Enter name:')
    if search_name:
        filtered_users = [user_info for user_info in user_index.values() if user_info['name'].lower().startswith(search_name.lower())]
    else:
        filtered_users = []
elif search_option == 'By Roll Number':
    search_roll = st.sidebar.text_input('Enter roll number:')
    if search_roll:
        # Filter users with roll numbers starting with the entered query (prefix match)
        filtered_users = [user_info for user_info in user_index.values() if user_info['roll'].lower().startswith(search_roll.lower())]
    else:
        filtered_users = []

# Display valid roll numbers/names as hyperlinks with proper routing
for user_info in filtered_users:
    user_link = generate_user_link(user_info)
    st.sidebar.markdown(user_link, unsafe_allow_html=True)

# Extract the route parameter
route_param = st.experimental_get_query_params().get('rollnumber', [None])[0]  # Corrected route parameter name
# Page 2: View Testimonials for Selected User (Right pat)
if route_param and route_param in user_index:
    with open('compiled.json', 'r') as compiled_file:
        compiled_data = json.load(compiled_file)
        testimonials = compiled_data.get(route_param, {})
    st.markdown(f'Selected User: {generate_user_link(user_index[route_param])}', unsafe_allow_html=True)
    #     # Load and display testimonials when a user is selected

    st.subheader('User Testimonials')
    tabs = st.tabs(["Testimonials Received", "Testimonials Given"])
    with tabs[0]:
        for testimonial in testimonials.get('testimonials_to', {}):
            st.markdown(f"From: {generate_user_link(user_index[testimonial['by_roll']])}", unsafe_allow_html=True)
            st.markdown(format_html(testimonial['testimonial']), unsafe_allow_html=True)  # Display testimonials as HTML
            st.write('---')

    with tabs[1]:
        for testimonial in testimonials.get('testimonials_from', {}):
            st.markdown(f"To: {generate_user_link(user_index[testimonial['to_roll']])}", unsafe_allow_html=True)
            st.markdown(format_html(testimonial['testimonial']), unsafe_allow_html=True)  # Display testimonials as HTML
            st.write('---')
else:
    st.subheader("No roll number/invalid user")
    st.sidebar.subheader('No User Selected')  # Show this message on the left when no user is selected

# Run the Streamlit app
if __name__ == '__main__':
    # Remove st.set_page_config to resolve the error
    pass

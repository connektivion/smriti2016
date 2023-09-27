import streamlit as st
import json
import html
import re

# Streamlit caching for reading JSON files
@st.cache_data
def load_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

# Preprocess the data
def preprocess_data():
    names_data = load_json('names.json')
    user_index = {info['roll']: info for info in names_data['names']}
    return user_index

# Function to generate user links with proper routing
def generate_user_link(user_info):
    return f"<a href='?rollnumber={user_info['roll']}' target='_self' rel='noopener noreferrer'>{user_info['name']} ({user_info['roll']})</a>"

# Function to format HTML
def format_html(input_text):
    def replace_html_entities(match):
        return html.unescape(match.group(0))

    def replace_unicode_escapes(match):
        return chr(int(match.group(1), 16))

    processed_text = re.sub(r'&[a-zA-Z]+;', replace_html_entities, input_text)
    processed_text = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode_escapes, processed_text)
    processed_text = processed_text.replace('\\n', '<br>')
    return processed_text

# Streamlit app
@st.cache_resource
def apply_style():
    with open( "style.css" ) as css:
        st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

def main():
    apply_style()
    st.title('Testimonial Viewer')
    
    # Create the header outside of the tabs

    # Page 1: Search for Users (Left part)
    st.header('Search for User')
    search_option = st.radio('Select search option:', ['By Name', 'By Roll Number'])

    user_index = preprocess_data()

    if search_option == 'By Name':
        search_name = st.text_input('Enter name:')
        filtered_users = [info for info in user_index.values() if info['name'].lower().startswith(search_name.lower())] if search_name else []
    elif search_option == 'By Roll Number':
        search_roll = st.text_input('Enter roll number:')
        filtered_users = [info for info in user_index.values() if info['roll'].lower().startswith(search_roll.lower())] if search_roll else []

    # Display valid roll numbers/names as hyperlinks with proper routing
    for user_info in filtered_users:
        user_link = generate_user_link(user_info)
        st.markdown(user_link, unsafe_allow_html=True)

    # Extract the route parameter
    route_param = st.experimental_get_query_params().get('rollnumber', [None])[0]

    # Page 2: View Testimonials for Selected User (Right part)
    if route_param and route_param in user_index:
        compiled_data = load_json('compiled.json')
        testimonials = compiled_data.get(route_param, {})
        selected_user_info = user_index[route_param]
        
        # Display the selected user's information
        st.markdown(f'Selected User: {generate_user_link(selected_user_info)}', unsafe_allow_html=True)

        # Create a container for the testimonial content under tabs
        testimonial_container = st.empty()

        st.subheader('User Testimonials')
        tabs = st.tabs(["Testimonials Received", "Testimonials Given"])
        
        for tab_index, testimonial_type in enumerate(["testimonials_to", "testimonials_from"]):
            with tabs[tab_index]:
                for testimonial in testimonials.get(testimonial_type, {}):
                    target_user_info = user_index[testimonial['by_roll']] if testimonial_type == "testimonials_to" else user_index[testimonial['to_roll']]
                    st.markdown(f"{'From' if testimonial_type == 'testimonials_to' else 'To'}: {generate_user_link(target_user_info)}", unsafe_allow_html=True)
                    st.markdown(format_html(testimonial['testimonial']), unsafe_allow_html=True)
                    st.write('---')
    
    else:
        st.subheader("No roll number/invalid user")

    # st.markdown(
    #     """
    #     <style>
    #     /* Add custom CSS to style the fixed button */
    #     .fixed-button {
            
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
    st.markdown("""
        <style>
            .element-container:has(#button-after) + div a button {
                position: fixed;
                bottom: 150px;
                right: 20px;
                opacity: 0.5;
                border-radius: 10px;
            }
        </style>""", unsafe_allow_html=True)

    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    st.markdown('''<a target="_self" href="#testimonial-viewer"><button>Scroll to Top</button></a>''', unsafe_allow_html=True)

if __name__ == '__main__':
    st.set_page_config(page_title="Smriti 2016 nitk", page_icon=":memo:")
    main()
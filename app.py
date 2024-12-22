import streamlit as st
from openai import OpenAI
from base64 import b64encode

def encode_image(uploaded_file):
    return b64encode(uploaded_file.getvalue()).decode("utf-8")

def extract_pancard_info(image_data, client):
    response = client.chat.completions.create(
        model= st.session_state["openai_model"],
        messages= [
            {
                "role": "system",
                "content": "You are a helpful assistant that extract data from pan card images in format in format {name : '',father_name: '',dob: '',pan: ''}"
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "Read pancard, dob and name from this pan card image in format {name : '',father_name: '',dob: '',pan: ''}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        stream=True,
        max_tokens=1000
    )
    return response

def extract_adhaar_front(image_data, client):
    response = client.chat.completions.create(
        model= st.session_state["openai_model"],
        messages= [
            {
                "role": "system",
                "content": "You are a helpful assistant that extract data from adhaar card image"
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "Read name, dob, gender, adhaar no. from this adhaar card image in format {name : '',dob: '',gender: '',adhaar_number: ''}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        stream=True,
        max_tokens=1000
    )
    return response

def extract_adhaar_back(image_data, client):
    response = client.chat.completions.create(
        model= st.session_state["openai_model"],
        messages= [
            {
                "role": "system",
                "content": "You are a helpful assistant that extract data from adhaar card image"
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "Read address, adhaar no. from this adhaar card image in format { address : '', adhaar_number: '' }"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        stream=True,
        max_tokens=1000
    )
    return response

def main():
    st.set_page_config(page_title='Lending App - Bahi Khata', layout = 'wide')
    st.title("Lending App")
    
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"
    
    col1, col2, col3 = st.columns(3)

    with col1:
        # Upload pancard 
        pancard_file = st.file_uploader("Upload PAN CARD", type=['png', 'jpg', 'jpeg'], help="Upload Pan card image ")
        if pancard_file is not None:
            #st.image(pancard_file, caption="PAN CARD", use_container_width=True)
            response = extract_pancard_info(encode_image(pancard_file), client)
            st.write_stream(response)

    with col2:
        # Upload adhaar card front & back
        adhaar_front = st.file_uploader("Upload ADHAAR(Front)", type=['png', 'jpg', 'jpeg'])
        if adhaar_front is not None:
            st.image(adhaar_front, caption="Adhaar (Front)", use_container_width=True)
            response = extract_adhaar_front(encode_image(adhaar_front), client)
            st.write_stream(response)

    with col3:
        adhaar_back = st.file_uploader("Upload ADHAAR(Back)", type=['png', 'jpg', 'jpeg'])
        if adhaar_back is not None:
            st.image(adhaar_back, caption="Adhaar (Back)", use_container_width=True)
            response = extract_adhaar_back(encode_image(adhaar_back), client)
            st.write_stream(response)

if __name__ == "__main__":
    main()
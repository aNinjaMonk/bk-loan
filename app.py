import streamlit as st
from openai import OpenAI
from base64 import b64encode
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

def encode_image(uploaded_file):
    return b64encode(uploaded_file.getvalue()).decode("utf-8")

def extract_pancard_info(image_data, client):
    response = client.chat.completions.create(
        model= st.session_state["openai_model"],
        messages= [
            {
                "role": "system",
                "content": "You are an assistant that extracts data from PAN card images. Return data in valid JSON format only."
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": 'Extract and return ONLY the following JSON: {"name" : "","father_name": "","dob": "","pan": ""}'
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
                "content": "You are a helpful assistant that extract data from adhaar card image. Return data in valid JSON format only."
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": 'Extract and return ONLY the following JSON: {"name" : "","dob": "","gender": "","adhaar_number": ""}'
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
                "content": "You are a helpful assistant that extract data from adhaar card image. Return data in valid JSON format only."
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": 'Read address, adhaar no. from this adhaar card image in format { "address" : "", "adhaar_number"": "" }'
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

def convertStream2JSON(_stream):
    # Convert Stream to string
    try:
        data_string = ""
        for chunk in _stream:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                data_string += chunk.choices[0].delta.content
        
        # Find JSON in the string
        start_idx = data_string.find('{')
        end_idx = data_string.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = data_string[start_idx:end_idx]
            # Clean the string
            json_str = json_str.replace("'", '"').strip()
            json_data = json.loads(json_str)
            
            return json_data
        else:
            return {}
        
    except json.JSONDecodeError as e:
        st.error(f"JSON Parse Error: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"Other error: {str(e)}")
        return {}

def getKYC():
    # Check if all required files are uploaded
    if 'pancard_file' not in st.session_state or st.session_state.pancard_file is None:
        st.error("Please upload PAN Card")
        return
    if 'adhaar_front' not in st.session_state or st.session_state.adhaar_front is None:
        st.error("Please upload Aadhaar Front")
        return
    if 'adhaar_back' not in st.session_state or st.session_state.adhaar_back is None:
        st.error("Please upload Aadhaar Back")
        return

    pancard_file = st.session_state.pancard_file
    adhaar_front = st.session_state.adhaar_front
    adhaar_back = st.session_state.adhaar_back
    data = {}

    # Process the files
    adhaar_back_data = extract_adhaar_back(encode_image(adhaar_back), client)
    adhaar_back_json = convertStream2JSON(adhaar_back_data)
    
    adhaar_front_data = extract_adhaar_front(encode_image(adhaar_front), client)
    adhaar_front_json = convertStream2JSON(adhaar_front_data)
    
    pan_data = extract_pancard_info(encode_image(pancard_file), client)
    pan_json = convertStream2JSON(pan_data)

    data = {
        "name": pan_json["name"],
        "father_name": pan_json["father_name"],
        "gender": adhaar_front_json["gender"],
        "dob": pan_json["dob"],
        "pan": pan_json["pan"],
        "adhaar": adhaar_front_json["adhaar_number"],
        "address": adhaar_back_json["address"]
    }

    st.write(data)

def reset():
    
    # Clear the session state completely
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def KYCForm():
    # Initialize session state for files if not exists
    if "files_uploaded" not in st.session_state:
        st.session_state.files_uploaded = False

    with st.expander("Owner Detail(s)", expanded=True, icon=":material/thumb_up:"):
        # File uploaders outside the form
        col1, col2, col3 = st.columns(3)
        with col1:
            pancard_file = st.file_uploader("Upload PAN CARD *", 
                                        type=['png', 'jpg', 'jpeg'], 
                                        help="Required: Upload Pan card image",
                                        key='pancard_file')

        with col2:
            adhaar_front = st.file_uploader("Upload ADHAAR(Front) *", 
                                        type=['png', 'jpg', 'jpeg'],
                                        help="Required: Upload Aadhaar front side",
                                        key='adhaar_front')

        with col3:
            adhaar_back = st.file_uploader("Upload ADHAAR(Back) *", 
                                        type=['png', 'jpg', 'jpeg'],
                                        help="Required: Upload Aadhaar back side",
                                        key='adhaar_back')

        # Update files_uploaded state
        st.session_state.files_uploaded = bool(pancard_file and adhaar_front and adhaar_back)

        # Form for submit button
        with st.form("kyc_form", clear_on_submit=True, border=False):
            submitted = st.form_submit_button("Get KYC", 
                                            use_container_width=True, 
                                            disabled=not st.session_state.files_uploaded)
            
            if submitted and st.session_state.files_uploaded:
                getKYC()

    with st.expander("Business Detail(s)", expanded=False, icon=":material/people:"):
        col1, col2 = st.columns(2)
        with col1:
            gst_file = st.file_uploader("Upload GST Document *", 
                                        type=['pdf'], 
                                        help="Required: Upload GST Certificate",
                                        key='gst_file')
        with col2:
            address_file = st.file_uploader("Upload Latest Electricity Bill *", 
                                        type=['jpg', 'jpeg', 'png', 'pdf'], 
                                        help="Required: Upload Latest Electricity Bill",
                                        key="address_file")

    with st.expander("Other Details", expanded=False):
        st.write("Available Soon")
        
def main():
    st.set_page_config(page_title='Lending App - Bahi Khata', layout = 'wide')
    st.title("Lending App")
    st.info("Please upload all required documents marked with *")
    
    
    tab1, tab2, tab3 = st.tabs(["KYC", "Banking", "Credit Bureau"])

    with tab1:
        KYCForm()

if __name__ == "__main__":
    main()
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from io import BytesIO
from PIL import Image
import streamlit as st
import base64

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Missing GOOGLE_API_KEY in .env")
    st.stop()

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Streamlit page config and style
st.set_page_config(page_title="Creative Image Generator", page_icon="🎨")

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #1e1e2f, #3b0f74);
    color: #ddd;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
h1 {
    color: #bb86fc;
    text-align: center;
    margin-bottom: 0.5rem;
}
.generated-image img {
    max-width: 100%;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(117, 81, 255, 0.5);
    border: 2px solid #a47aff;
    display: block;
    margin-left: auto;
    margin-right: auto;
}
footer {
    text-align: center;
    font-size: 0.9rem;
    color: #aaa;
    margin-top: 3rem;
}
.prompt-container {
    margin-bottom: 1rem;
}
.generate-btn {
    background-color: #7b5cff;
    color: white;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
}
.generate-btn:hover {
    background-color: #a47aff;
}
</style>
""", unsafe_allow_html=True)

st.title("🎨 Creative Image Generator with Gemini")

# Prompt input area
prompt = st.text_area(
    "Enter your creative image prompt below:",
    placeholder="Type something like: 'A futuristic city skyline at sunset, vibrant colors'",
    height=140,
)

if st.button("Generate Image"):
    if not prompt.strip():
        st.warning("Please enter a prompt to generate an image.")
    else:
        with st.spinner("Generating image..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"]
                    )
                )

                # Extract image bytes
                img_bytes = None
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        img_bytes = part.inline_data.data
                        break

                if img_bytes:
                    img = Image.open(BytesIO(img_bytes))

                    # Encode image as base64
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()

                    # Show styled image
                    img_html = f'''
                    <div class="generated-image">
                        <img src="data:image/png;base64,{img_str}" alt="Generated Image" />
                    </div>
                    '''
                    st.markdown(img_html, unsafe_allow_html=True)

                else:
                    st.error("No image data received from the API.")

            except Exception as e:
                st.error(f"Error generating image: {e}")

st.markdown('<footer>Powered by Google Gemini API & Streamlit</footer>', unsafe_allow_html=True)
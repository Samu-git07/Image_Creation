import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from langdetect import detect
from langcodes import Language
from gtts import gTTS
import base64
import tempfile

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file.")
    st.stop()

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Streamlit page setup
st.set_page_config(page_title="Multilingual Text Summariser", layout="centered")
st.title("🌐 Multilingual Text Summariser using Gemini 2.5")

# Text input
input_text = st.text_area("✍️ Enter text in any language:", height=250)

# Summary length control
length_option = st.radio("📏 Choose Summary Length:", ["Brief", "Medium", "Detailed"], index=1)
length_map = {
    "Brief": "in 2-3 sentences",
    "Medium": "in about 5 sentences",
    "Detailed": "in a detailed paragraph"
}

# Target language
target_lang = st.selectbox(
    "🌐 Translate Summary To:",
    ["Same as input", "English", "Hindi", "Spanish", "French", "German", "Malayalam", "Kannada", "Tamil"]
)


# Summarise button
if st.button("🧠 Summarise"):
    if not input_text.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            # Detect language
            detected_lang_code = detect(input_text)
            detected_lang_name = Language.get(detected_lang_code).display_name()
            st.info(f"🔍 Detected Language: `{detected_lang_name}` ({detected_lang_code})")

            # Summarisation prompt
            summarise_prompt = f"Summarise the following text {length_map[length_option]}:\n\n{input_text}"
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-05-20",
                contents=[summarise_prompt]
            )
            summary = response.text.strip()

            # Translate if needed
            if target_lang != "Same as input":
                translate_prompt = f"Translate the following summary to {target_lang}:\n\n{summary}"
                translated = client.models.generate_content(
                    model="gemini-2.5-flash-preview-05-20",
                    contents=[translate_prompt]
                )
                summary = translated.text.strip()
                st.success(f"📄 Translated Summary ({target_lang}):")
            else:
                st.success("📄 Summary:")

            # Show summary
            st.write(summary)

            # Summary stats
            orig_len = len(input_text.split())
            sum_len = len(summary.split())
            compression = round((sum_len / orig_len) * 100, 2)
            st.markdown("---")
            st.markdown("### 📊 Summary Stats")
            st.write(f"🔸 Original Length: `{orig_len}` words")
            st.write(f"🔹 Summary Length: `{sum_len}` words")
            st.write(f"📉 Compression Ratio: `{compression}%`")

            # Download link
            b64 = base64.b64encode(summary.encode()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="summary.txt">📥 Download Summary as TXT</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Text-to-Speech
            st.markdown("---")
            st.markdown("### 🔊 Listen to Summary")

            try:
                # Map readable language to gTTS code
                language_map = {
                  "English": "en",
                    "Hindi": "hi",
                    "Spanish": "es",
                    "French": "fr",
                    "German": "de",
                    "Malayalam": "ml",
                    "Kannada": "kn",
                    "Tamil": "ta"
                }


                lang_for_tts = language_map.get(target_lang, detected_lang_code[:2])
                st.write(f"🔈 Using language code for TTS: `{lang_for_tts}`")

                # Generate and play audio
                tts = gTTS(text=summary, lang=lang_for_tts)

                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tts.save(tmp_file.name)
                    tmp_file_path = tmp_file.name

                # Load and play audio
                with open(tmp_file_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")

            except ValueError as ve:
                st.error(f"⚠️ TTS Language Error: {ve}. Try selecting English or Hindi.")
            except Exception as e:
                st.error(f"⚠️ Audio generation failed. Error: {e}")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
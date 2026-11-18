import streamlit as st
import pandas as pd
import os
from google import genai
from google.genai import types
from io import StringIO

st.set_page_config(page_title="Camara Gemini Live Extractor")
st.title("Camara Attendance Extractor - Powered by Gemini AI")
st.write("Mfumo wa mtandaoni (Live) wa kuchakata fomu za CamScanner kwa kasi na ufanisi wa juu.")

# Sehemu ya kuweka API Key kwenye Sidebar ya app yako
st.sidebar.header("Mipangilio ya AI")
api_key_input = st.sidebar.text_input("Weka Gemini API Key Yako:", type="password", help="Weka API Key yako hapa.")

uploaded_file = st.file_uploader("Pakia Fomu ya Mahudhurio (PDF)", type=["pdf"])
role_choice = st.selectbox("Chagua Kategoria:", ["Teacher", "Student"])

if uploaded_file is not None:
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    if st.button("Chakata kwa Kasi (Fast Process)"):
        if not api_key_input:
            st.error("Tafadhali weka Gemini API Key yako kwenye kisanduku cha upande wa kushoto.")
        else:
            with st.spinner("Inachakata kwa kasi... Tafadhali subiri kidogo."):
                try:
                    client = genai.Client(api_key=api_key_input)
                    pdf_bytes = uploaded_file.read()
                    
                    # Prompt fupi na ya moja kwa moja ili kuongeza kasi ya majibu
                    prompt = f"""
                    Soma fomu hii ya {role_choice} na utoe orodha ya watu wote kwa mfumo wa safu (CSV) zenye vichwa hivi pekee:
                    Full Name,Phone,Email,Position
                    
                    Kanuni:
                    - Full Name: Jina kamili bila maneno ya ziada.
                    - Phone: Namba ya simu ya Tanzania inayoanza na 06 au 07 (acha wazi kama hakuna).
                    - Email: Weka tupu.
                    - Position: Andika "{role_choice}" isipokuwa kama ni mkuu wa shule andika "Head Master".
                    
                    Toa data za CSV pekee bila maelezo ya ziada.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=[
                            types.Part.from_bytes(
                                data=pdf_bytes,
                                mime_type='application/pdf',
                            ),
                            prompt
                        ]
                    )
                    
                    csv_text = response.text.strip()
                    if "```csv" in csv_text:
                        csv_text = csv_text.split("```csv")[1].split("```")[0].strip()
                    elif "```" in csv_text:
                        csv_text = csv_text.split("```")[1].split("```")[0].strip()
                        
                    df = pd.read_csv(StringIO(csv_text))
                    
                    if not df.empty:
                        st.success(f"Imefanikiwa! Imepatikana kumbukumbu {len(df)}.")
                        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                        
                        csv_data = edited_df.to_csv(index=False).encode('utf-8')
                        final_csv_name = f"{original_filename}.csv"
                        
                        st.download_button(
                            label=f"Pakua Faili la CSV ({final_csv_name})",
                            data=csv_data,
                            file_name=final_csv_name,
                            mime="text/csv",
                        )
                    else:
                        st.warning("Hakuna taarifa za kutosha zilizopatikana.")
                except Exception as e:
                    st.error(f"Hitilafu imetokea: {e}")
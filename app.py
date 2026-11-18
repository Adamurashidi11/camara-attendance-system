import streamlit as st
import pandas as pd
import os
from google import genai
from google.genai import types
from io import StringIO

st.set_page_config(page_title="Camara Gemini Live Extractor")
st.title("Camara Attendance Extractor - Powered by Gemini AI")
st.write("Mfumo wa mtandaoni (Live) wa kuchakata fomu za CamScanner kwa kutumia uwezo wa juu wa Gemini AI.")

# Sehemu ya kuweka API Key kwenye Sidebar ya app yako
st.sidebar.header("Mipangilio ya AI")
api_key_input = st.sidebar.text_input("Weka Gemini API Key Yako:", type="password", help="Weka API Key yako uliyochukua Google AI Studio hapa.")

uploaded_file = st.file_uploader("Pakia Fomu ya Mahudhurio (PDF)", type=["pdf"])
role_choice = st.selectbox("Chagua Kategoria:", ["Teacher", "Student"])

if uploaded_file is not None:
    original_filename = os.path.splitext(uploaded_file.name)[0]
    
    if st.button("Chakata Kupitia Gemini AI"):
        if not api_key_input:
            st.error("Tafadhali weka Gemini API Key yako kwenye kisanduku cha upande wa kushoto (Sidebar) ndipo uendelee.")
        else:
            with st.spinner("Gemini AI inasoma fomu yako na kupanga kila kitu... Subiri sekunde chache."):
                try:
                    # Anzisha mteja wa Gemini
                    client = genai.Client(api_key=api_key_input)
                    
                    pdf_bytes = uploaded_file.read()
                    
                    prompt = f"""
                    Hili ni faili la fomu ya mahudhurio ya Shule ya Camara (kategoria: {role_choice}).
                    Tafadhali soma kurasa zote za PDF hii kwa umakini mkubwa (hata kama ni picha za CamScanner zilizochakaa au kuandikwa kwa mkono).
                    
                    Tafuta na utoe orodha ya watu wote waliomo kwenye fomu hii ukitengeneza safu zifuatazo pekee:
1. Full Name (Jina kamili la mtu, ondoa maneno ya ziada kama jina la shule au madaraja).
2. Phone (Namba ya simu ya Tanzania inayoanza na 06 au 07. Kama ni mwanafunzi na hakuna namba kwenye fomu, acha wazi au uweke tupu).
3. Email (Weka tupu kwa sasa).
4. Position (Weka neno "{role_choice}" isipokuwa kama picha imeandikwa wazi kuwa ni mkuu wa shule, basi andika "Head Master").
                    
                    Rudisha majibu yako YOTE kwa mfumo wa CSV safi kabisa yenye kichwa cha habari (Header): Full Name,Phone,Email,Position. Usiandike maelezo mengine yoyote ya ziada, toa data za CSV pekee.
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
                        st.success(f"Gemini AI imefanikiwa kusoma na kuchomoa kumbukumbu {len(df)} kwa ufasaha mkubwa.")
                        
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
                        st.warning("Gemini haijapata taarifa za kutosha kwenye fomu hii.")
                except Exception as e:
                    st.error(f"Hitilafu imetokea wakati wa kuwasiliana na AI: {e}")
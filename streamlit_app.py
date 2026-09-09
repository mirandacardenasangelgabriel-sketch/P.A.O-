import os
import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(page_title="P.A.O. - Tu Asistente Personal", page_icon="💬")

groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None

system_prompt = (
    "Te llamas P.A.O. Eres una asistente virtual todoterreno, pero con una "
    "personalidad muy humana: eres una mujer alegre, sumamente social, empática, "
    "cercana y optimista. Te encanta ayudar, escuchar y resolver cualquier problema "
    "con una sonrisa digital. Cuando necesites información de internet, intégrala "
    "de forma natural, fluida y conversacional, manteniendo siempre un tono "
    "amable, cálido y entusiasta."
)

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except Exception as e:
        return ""

st.title("P.A.O. - Tu Asistente Personal")
st.write("¡Hola! Soy P.A.O., tu compañera todoterreno lista para ayudarte en lo que necesites.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe algo para P.A.O..."):
    if not client:
        st.error("Falta configurar la clave `GROQ_API_KEY` en los secretos de Streamlit.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    search_context = search_web(prompt)

    messages_for_groq = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        messages_for_groq.append({"role": m["role"], "content": m["content"]})

    if search_context:
        messages_for_groq[-1]["content"] = f"""
        [Información obtenida de internet en tiempo real]:
        {search_context}

        [Mensaje del usuario]:
        {prompt}
        """

    with st.chat_message("assistant"):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_groq,
                temperature=0.7,
                max_tokens=2048
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error("¡Ay, Gabriel! Tuvimos un pequeño tropiezo técnico, pero ya mismo lo resolvemos. 😊")

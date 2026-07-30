print("🔥 APP.PY IS LOADING")
import streamlit as st
from rag import ask_question, clear_chat

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family:'Poppins',sans-serif;
}

/* Background */

.stApp{
background:
linear-gradient(135deg,#0f172a,#111827,#1e3a8a,#312e81);
background-size:400% 400%;
animation:gradientBG 15s ease infinite;
color:white;
}

@keyframes gradientBG{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

/* Hide Streamlit Header */

header{
visibility:hidden;
}

footer{
visibility:hidden;
}

/* Sidebar */

section[data-testid="stSidebar"]{
background:rgba(17,24,39,.65);
backdrop-filter:blur(20px);
border-right:1px solid rgba(255,255,255,.1);
}

/* Hero Card */

.hero{

background:rgba(255,255,255,.08);

padding:35px;

border-radius:25px;

backdrop-filter:blur(18px);

border:1px solid rgba(255,255,255,.15);

box-shadow:0 8px 30px rgba(0,0,0,.35);

margin-bottom:30px;

text-align:center;

}

/* Hero Title */

.hero h1{

font-size:48px;

font-weight:700;

background:linear-gradient(90deg,#60a5fa,#38bdf8,#818cf8,#f472b6);

-webkit-background-clip:text;

-webkit-text-fill-color:transparent;

margin-bottom:10px;

}

/* Hero Subtitle */

.hero p{

font-size:18px;

color:#d1d5db;

margin-top:0;

}

/* Chat Bubble */

.chat-card{

background:rgba(255,255,255,.08);

padding:18px;

border-radius:18px;

backdrop-filter:blur(15px);

border:1px solid rgba(255,255,255,.12);

margin-bottom:18px;

box-shadow:0 5px 18px rgba(0,0,0,.25);

}

/* Source Card */

.source-card{

background:rgba(59,130,246,.12);

padding:12px;

border-radius:14px;

margin-top:10px;

border-left:5px solid #60a5fa;

}

/* Buttons */

.stButton>button{

width:100%;

border:none;

border-radius:12px;

padding:12px;

font-weight:600;

background:linear-gradient(90deg,#3b82f6,#8b5cf6);

color:white;

transition:.3s;

}

.stButton>button:hover{

transform:scale(1.02);

box-shadow:0 5px 18px rgba(59,130,246,.5);

}

/* Input */

textarea{

background:rgba(255,255,255,.08)!important;

color:white!important;

border-radius:15px!important;

}

</style>
""",unsafe_allow_html=True)

# ==========================================================
# SESSION STATE
# ==========================================================

if "messages" not in st.session_state:
    st.session_state.messages=[]

# ==========================================================
# HERO SECTION
# ==========================================================

st.markdown("""

<div class="hero">

<h1>🤖 Enterprise Knowledge Assistant</h1>

<p>
AI Powered Enterprise Document Intelligence
</p>

</div>

""",unsafe_allow_html=True)
# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown("## ⚙️ Control Panel")

    st.success("🟢 Enterprise AI Online")

    st.markdown("---")

    st.metric(
        label="📄 Documents",
        value="170+"
    )

    st.metric(
        label="🧠 AI Model",
        value="Llama 3.3"
    )

    st.metric(
        label="⚡ Vector Store",
        value="FAISS"
    )

    st.metric(
        label="🔍 Embeddings",
        value="BGE Base"
    )

    st.markdown("---")

    st.info(
        """
### 💡 Try asking

• Leave Policy

• Work From Home

• Medical Insurance

• IT Policy

• Dress Code

• Employee Benefits
"""
    )

    st.markdown("---")

    if st.button("🗑 Clear Conversation"):

        clear_chat()

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    st.caption(
        "Enterprise Knowledge Assistant\n\n"
        "Powered by LangChain • Groq • FAISS"
    )


# ==========================================================
# WELCOME MESSAGE
# ==========================================================

if len(st.session_state.messages) == 0:

    with st.chat_message("assistant"):

        st.markdown(
            """
👋 **Welcome!**

I'm your **Enterprise Knowledge Assistant**.

I can answer questions about:

- 📄 HR Policies
- 🏖 Leave Policies
- 💼 Employee Benefits
- 🏠 Work From Home
- 🔒 Company Guidelines
- 💻 IT Policies

Ask me anything below.
"""
        )


# ==========================================================
# DISPLAY CHAT HISTORY
# ==========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            st.markdown("#### 📚 Sources")

            for source in message["sources"]:

                st.markdown(
                    f"""
<div class="source-card">

<b>📄 {source['file']}</b><br>

Page: {source['page']}

</div>
""",
                    unsafe_allow_html=True
                )
# ==========================================================
# CHAT INPUT
# ==========================================================

prompt = st.chat_input(
    "💬 Ask anything about your company documents..."
)

if prompt:

    # ---------------------------------------
    # Display User Message
    # ---------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # ---------------------------------------
    # Generate AI Response
    # ---------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("🤖 Thinking..."):

            try:

                result = ask_question(prompt)

                answer = result.get(
                    "answer",
                    "Sorry, I couldn't generate an answer."
                )

                sources = result.get(
                    "sources",
                    []
                )

            except Exception as e:

                answer = (
                    "❌ An unexpected error occurred.\n\n"
                    f"**Details:** {e}"
                )

                sources = []

        st.markdown(answer)

        # ---------------------------------------
        # Display Sources
        # ---------------------------------------

        if sources:

            st.markdown("### 📚 Sources")

            for source in sources:

                filename = source.get(
                    "file",
                    "Unknown"
                )

                page = source.get(
                    "page",
                    "-"
                )

                st.markdown(
                    f"""
<div class="source-card">

<b>📄 {filename}</b><br>

📑 Page: {page}

</div>
""",
                    unsafe_allow_html=True
                )

    # ---------------------------------------
    # Save Assistant Response
    # ---------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )
# ==========================================================
# DOWNLOAD CHAT
# ==========================================================

if st.session_state.messages:

    conversation = ""

    for message in st.session_state.messages:

        role = (
            "USER"
            if message["role"] == "user"
            else "ASSISTANT"
        )

        conversation += f"{role}\n"
        conversation += "-" * 50 + "\n"
        conversation += message["content"] + "\n\n"

    st.sidebar.download_button(
        label="📥 Download Conversation",
        data=conversation,
        file_name="enterprise_chat.txt",
        mime="text/plain"
    )


# ==========================================================
# SIDEBAR FOOTER
# ==========================================================

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
### 🚀 Tech Stack

- 🦜 LangChain
- ⚡ Groq Llama 3.3
- 🔍 FAISS
- 🤗 HuggingFace
- 🎨 Streamlit

---
"""
)

st.sidebar.success("🟢 System Running")

st.sidebar.caption(
    "Enterprise Knowledge Assistant\n"
    "Version 1.0"
)


# ==========================================================
# PAGE FOOTER
# ==========================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown(
"""
<div style="text-align:center;
padding:25px;
margin-top:30px;
border-radius:20px;
background:rgba(255,255,255,0.05);
backdrop-filter:blur(15px);
border:1px solid rgba(255,255,255,0.08);">

<h4 style="color:#93c5fd;">
🤖 Enterprise Knowledge Assistant
</h4>

<p style="color:#cbd5e1;">

Powered by
<b>LangChain</b> •
<b>Groq</b> 
<b>FAISS</b> •
<b>HuggingFace</b> •
<b>Streamlit</b>

</p>

<p style="font-size:13px;color:#94a3b8;">

AI Powered Enterprise Document Intelligence

</p>

</div>
""",
unsafe_allow_html=True
)                    

# dashboards/app.py (Full App with Unique Selectbox Keys to Avoid StreamlitDuplicateElementId)

import streamlit as st
import pandas as pd
import os
import sys
import time
import random
from openai import OpenAI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.data_utils import load_dataframe
from agents.agent_profiles import AgentProfile, generate_random_agent
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="💉 Vaccine Hesitancy Simulator", layout="wide")

log_path = "data/simulation_log.csv"
fvr_log_path = "data/fake_vs_real_log.csv"
emo_log_path = "data/emotion_celebrity_log.csv"
os.makedirs("data", exist_ok=True)

st.markdown("<h1 style='color:#2c6df3'>💉 Vaccine Hesitancy Simulator</h1>", unsafe_allow_html=True)

tabs = st.tabs(["🧪 Simulation",
    "📊 Insights",
    "⚙️ Auto Mode",
    "📈 Fake vs Real",
    "🌟 Emotion & Celebrity",
    "🗣️ Chatbot",
    "👥 Team",])

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs

@st.cache_data
def load_tweets():
    return load_dataframe("tweets.csv")

def parse_binary_response(text):
    return "No" if "no" in text.lower() else "Yes"

def simulate_agent_final_response(agent: AgentProfile, context: str) -> str:
    system_prompt = f"You are simulating a person who is {agent.age_group}, {agent.personality}, has {agent.education_level} education, is from a {agent.socioeconomic_status} background, and initially is '{agent.prior_vaccine_belief}' about vaccines."
    user_prompt = f"Here are a number of social media posts about the COVID-19 vaccine:\n\n{context}\n\nBased on this, would you take the COVID-19 vaccine? Answer Yes or No only."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def log_simulation(agent, label, method="manual"):
    row = pd.DataFrame([{ 
        "education": agent.education_level,
        "income": agent.socioeconomic_status,
        "belief": agent.prior_vaccine_belief,
        "age": agent.age_group,
        "personality": agent.personality,
        "response": label,
        "method": method
    }])
    row.to_csv(log_path, mode='a', header=not os.path.exists(log_path), index=False)

def log_fvr(agent, label, pct):
    row = pd.DataFrame([{ 
        "education": agent.education_level,
        "income": agent.socioeconomic_status,
        "belief": agent.prior_vaccine_belief,
        "age": agent.age_group,
        "personality": agent.personality,
        "response": label,
        "real_pct": pct
    }])
    row.to_csv(fvr_log_path, mode='a', header=not os.path.exists(fvr_log_path), index=False)

def log_emotion_celebrity(agent, label, type_used):
    row = pd.DataFrame([{ 
        "education": agent.education_level,
        "income": agent.socioeconomic_status,
        "belief": agent.prior_vaccine_belief,
        "age": agent.age_group,
        "personality": agent.personality,
        "response": label,
        "influence_type": type_used
    }])
    row.to_csv(emo_log_path, mode='a', header=not os.path.exists(emo_log_path), index=False)

# === SIMULATION TAB ===
with tab1:
    st.sidebar.header("🧬 Build Your Agent")
    age = st.sidebar.selectbox("Select Age Group", ["young adult", "middle-aged", "senior"], key="sim_age")
    edu = st.sidebar.selectbox("Select Education Level", ["no education", "high school", "bachelor's", "master's", "PhD"], key="sim_edu")
    inc = st.sidebar.selectbox("Select Income Level", ["low", "middle", "high"], key="sim_inc")
    bel = st.sidebar.selectbox("Select Vaccine Belief", ["anti-vaccine", "neutral", "pro-vaccine"], key="sim_bel")
    pers = st.sidebar.selectbox("Select Personality", ["anxious", "skeptical", "indifferent", "cautious", "open-minded"], key="sim_pers")

    agent = AgentProfile("Custom Agent", edu, pers, bel, inc, age)

    st.sidebar.header("🧪 Simulation Controls")
    tweet_count = st.sidebar.slider("🔢 Tweet Count", 5, 50, 10)
    real_pct = st.sidebar.slider("📰 % Real Tweets", 0, 100, 70, step=10)
    run = st.sidebar.button("🚀 Simulate")

    if run:
        df = load_tweets()
        real_sample = df[df.label == "real"].sample(int(tweet_count * real_pct / 100))
        fake_sample = df[df.label == "fake"].sample(tweet_count - len(real_sample))
        context = "\n".join([f"- {row['tweet']}" for _, row in pd.concat([real_sample, fake_sample]).iterrows()])
        st.markdown("<h3>🧠 Final Agent Response</h3>", unsafe_allow_html=True)
        with st.spinner("Thinking like your agent..."):
            final_response = simulate_agent_final_response(agent, context)
            label = parse_binary_response(final_response)
            log_simulation(agent, label)
            st.markdown(f"<div style='padding:1rem 0;font-size:18px'>{final_response}</div>", unsafe_allow_html=True)

# === INSIGHTS TAB ===
with tab2:
    st.subheader("📊 Real-Time Insights")
    if os.path.exists(log_path):
        data = pd.read_csv(log_path)
        pie = data["response"].value_counts().reset_index()
        pie.columns = ["Response", "Count"]
        st.plotly_chart(px.pie(pie, values='Count', names='Response'))
        for col in ["education", "income", "belief", "age"]:
            dist = data.groupby(col)["response"].value_counts(normalize=True).unstack().fillna(0)
            if "Yes" in dist.columns:
                st.plotly_chart(px.bar(dist, y=dist.index, x="Yes", orientation='h', title=f"By {col}"), key=f"insight_{col}")

# === AUTO MODE TAB ===
with tab3:
    st.subheader("⚙️ Auto Simulation")
    auto_start = st.button("▶ Start Auto Simulation")
    auto_stop = st.button("⏹ End and Show Insights")
    batch = st.slider("Batch Size", 10, 1000, 50, step=10)
    tcount = st.slider("Tweets per Agent", 5, 30, 10)
    pct = st.slider("% Real Tweets", 0, 100, 70, step=10)

    if os.path.exists(log_path):
        run_count = pd.read_csv(log_path, on_bad_lines="skip").shape[0]
    else:
        run_count = 0

    st.markdown(f"### 🧮 Total Simulations Run: {run_count}")

    if auto_start:
        st.info("Running auto-simulations in background...")
        df = load_tweets()
        for _ in range(batch):
            agent = generate_random_agent()
            real = df[df.label == "real"].sample(int(tcount * pct / 100))
            fake = df[df.label == "fake"].sample(tcount - len(real))
            context = "\n".join([f"- {row['tweet']}" for _, row in pd.concat([real, fake]).iterrows()])
            label = parse_binary_response(simulate_agent_final_response(agent, context))
            log_simulation(agent, label, method="auto")
        st.success(f"Auto-simulated {batch} agents!")

    if auto_stop:
        st.subheader("📊 Insights After Auto Run")
        if os.path.exists(log_path):
            data = pd.read_csv(log_path, on_bad_lines="skip")
            pie = data["response"].value_counts().reset_index()
            pie.columns = ["Response", "Count"]
            st.plotly_chart(px.pie(pie, values='Count', names='Response'), key="auto_summary_pie")
            for col in ["education", "income", "belief", "age"]:
                dist = data.groupby(col)["response"].value_counts(normalize=True).unstack().fillna(0)
                if "Yes" in dist.columns:
                    st.plotly_chart(px.bar(dist, y=dist.index, x="Yes", orientation='h',
                                           title=f"By {col}"), key=f"auto_chart_{col}")
        else:
            st.warning("No auto run data available.")

# === FAKE VS REAL TAB ===
with tab4:
    st.subheader("📈 Fake vs Real Influence")
    col1, col2 = st.columns(2)
    with col1:
        age = st.selectbox("Age", ["young adult", "middle-aged", "old_aged"], key="fvr_age")
        edu = st.selectbox("Education", ["no education", "high school", "college", "bachelor", "master", "PhD"], key="fvr_edu")
        inc = st.selectbox("Income", ["low-income", "middle-income", "high-income"], key="fvr_inc")
    with col2:
        bel = st.selectbox("Belief", ["anti-vaccine", "neutral", "pro-vaccine"], key="fvr_bel")
        pers = st.selectbox("Personality", ["anxious", "skeptical", "indifferent", "cautious", "open-minded"], key="fvr_pers")
        reps = st.slider("Repeats per %", 1, 20, 5)
    total = st.slider("Tweets per Run", 1, 50, 20)
    go = st.button("Run Analysis")

    if go:
        agent = AgentProfile("FVR", edu, pers, bel, inc, age)
        df = load_tweets()
        records = []
        for pct in range(0, 101, 10):
            y = 0
            for i in range(reps):
                with st.spinner(f"{pct}% real news, run {i + 1}/{reps}..."):
                    r = df[df.label == "real"].sample(int(total * pct / 100))
                    f = df[df.label == "fake"].sample(total - len(r))
                    context = "\n".join([f"- {row['tweet']}" for _, row in pd.concat([r, f]).iterrows()])
                    label = parse_binary_response(simulate_agent_final_response(agent, context))
                    if label == "Yes":
                        y += 1
                    log_fvr(agent, label, pct)
            records.append({"Real %": pct, "Acceptance Rate": y / reps})
        if os.path.exists(fvr_log_path):
            df_log = pd.read_csv(fvr_log_path, on_bad_lines="skip")
            df_log = df_log[df_log["response"].isin(["Yes", "No"])]
            summary = (
                df_log.groupby("real_pct")["response"]
                .apply(lambda x: (x == "Yes").mean())
                .reset_index(name="Acceptance Rate")
            )
            st.plotly_chart(px.line(summary, x="real_pct", y="Acceptance Rate", markers=True,
                                    title="Overall Acceptance Rate vs. % Real News"), use_container_width=True)
        else:
            st.info("No logged results yet. Run an analysis.")

# === EMOTION & CELEBRITY TAB ===
with tab5:
    st.subheader("🌟 Emotion & Celebrity Influence")
    col1, col2 = st.columns(2)
    with col1:
        age = st.selectbox("Age Group", ["young adult", "middle-aged", "old_aged"], key="emo_age")
        edu = st.selectbox("Education", ["no education", "high school", "bachelor", "master", "PhD"], key="emo_edu")
        inc = st.selectbox("Income", ["low", "middle", "high"], key="emo_inc")
    with col2:
        bel = st.selectbox("Belief", ["anti-vaccine", "neutral", "pro-vaccine"], key="emo_bel")
        pers = st.selectbox("Personality", ["anxious", "skeptical", "indifferent", "cautious", "open-minded"], key="emo_pers")
        total_tweets = st.slider("Tweet Count", 5, 50, 20)
        real_pct = st.slider("Real Tweet %", 0, 100, 70, step=10)
    emo = st.checkbox("💔 Add Emotional Message")
    celeb = st.checkbox("🎤 Add Celebrity Message")
    run = st.button("🚀 Run")

    if run:
        agent = AgentProfile("Influence", edu, pers, bel, inc, age)
        df = load_tweets()
        real = df[df.label == "real"].sample(int(total_tweets * real_pct / 100))
        fake = df[df.label == "fake"].sample(total_tweets - len(real))
        tweets = pd.concat([real, fake])
        context = "\n".join([f"- {row['tweet']}" for _, row in tweets.iterrows()])
        if emo: context += "\n- A mother lost her baby after refusing a vaccine."
        if celeb: context += "\n- A celebrity posted their vaccine story, inspiring millions."
        response = simulate_agent_final_response(agent, context)
        label = parse_binary_response(response)
        st.markdown(f"<h4>{label} — {response}</h4>", unsafe_allow_html=True)
        if emo:
            log_emotion_celebrity(agent, label, "emotional")
        elif celeb:
            log_emotion_celebrity(agent, label, "celebrity")
        else:
            log_emotion_celebrity(agent, label, "none")

    if os.path.exists(emo_log_path):
        df = pd.read_csv(emo_log_path)
        for key in ["emotional", "celebrity"]:
            sub = df[df.influence_type == key]
            if not sub.empty:
                agg = sub["response"].value_counts(normalize=True).reset_index()
                agg.columns = ["Response", "Fraction"]
                st.plotly_chart(px.pie(agg, values='Fraction', names='Response', title=f"Effect of {key.title()} Messaging"))




with tab6:
    st.title("🗣️ Persuasive Chatbot Agent")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}

    # Step 1: Pre-chat user profile
    with st.form("user_profile_form"):
        st.subheader("🧬 Tell us a bit about yourself")
        col1, col2 = st.columns(2)
        with col1:
            age = st.selectbox("Your age group", ["young adult", "middle-aged", "senior"])
            edu = st.selectbox("Your education level", ["no education", "high school", "college", "bachelor", "master", "PhD"])
            inc = st.selectbox("Your income level", ["low-income", "middle-income", "high-income"])
        with col2:
            belief = st.selectbox("Your belief about vaccines", ["anti-vaccine", "neutral", "pro-vaccine"])
            pers = st.selectbox("Your personality", ["anxious", "skeptical", "indifferent", "cautious", "open-minded"])
            concern = st.text_area("What worries you about the vaccine?")
        submit = st.form_submit_button("Start Chat")

    if submit:
        st.session_state.user_profile = {
            "age": age,
            "edu": edu,
            "income": inc,
            "belief": belief,
            "personality": pers,
            "concern": concern
        }
        st.session_state.chat_history = []

    # Step 2: Generate system prompt if ready
    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        system_prompt = (
            f"You are a warm, empathetic vaccine expert who speaks in an understanding tone. "
            f"You're speaking to a {profile['personality']} person who is {profile['age']}, with {profile['edu']} education, "
            f"from a {profile['income']} background, and they currently feel '{profile['belief']}' about vaccines."
        )
        if profile["concern"]:
            system_prompt += f" Their concern is: {profile['concern']}."
        system_prompt += " Your job is to have a helpful and honest conversation, using emotional stories or examples of celebrities who vaccinated, and gently persuade them to consider vaccination."

        # Step 3: Chat Interface
        st.divider()
        st.markdown("### 🤖 Chat with the Vaccine Assistant")
        for entry in st.session_state.chat_history:
            st.chat_message(entry["role"]).markdown(entry["content"])

        user_input = st.chat_input("Your message...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            messages = [
                {"role": "system", "content": system_prompt}
            ] + st.session_state.chat_history[-10:]

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                reply = f"⚠️ Error: {e}"

            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").markdown(reply)


# === TEAM TAB ===
with tab7:
    st.markdown("""
    ### 👥 Team Members
    - Amir Pilehvarian (Lead Developer)
    - Partner 1 (Data Scientist)
    - Partner 2 (Public Health Analyst)
    - Partner 3 (LLM Engineer)

    ### 🧭 Project Goals
    - Simulate agent-based vaccine hesitancy
    - Study misinformation, peer influence, and media types
    - Build interactive public health AI toolkits
    """)

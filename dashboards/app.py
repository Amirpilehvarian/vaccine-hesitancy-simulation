# dashboards/app.py (Full Version with Simulation, Insights, Auto Mode, Fake vs Real Tabs Only)

import streamlit as st
import pandas as pd
import os
import re
import time
import random
from openai import OpenAI
from utils.data_utils import load_dataframe
from agents.agent_profiles import AgentProfile, generate_random_agent
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="💉 Vaccine Hesitancy Simulator", layout="wide")

log_path = "data/simulation_log.csv"
os.makedirs("data", exist_ok=True)

st.markdown("<h1 style='color:#2c6df3'>💉 Vaccine Hesitancy Simulator</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧪 Simulation", "📊 Insights", "⚙️ Auto Mode", "📈 Fake vs Real", "👥 Team"])

@st.cache_data
def load_tweets():
    return load_dataframe("tweets.csv")

def parse_binary_response(text):
    return "No" if "no" in text.lower() else "Yes"

def simulate_agent_final_response(agent: AgentProfile, context: str) -> str:
    system_prompt = (
        f"You are simulating a person who is {agent.age_group}, {agent.personality}, has {agent.education_level} education, "
        f"is from a {agent.socioeconomic_status} background, and initially is '{agent.prior_vaccine_belief}' about vaccines."
    )
    user_prompt = (
        f"Here are a number of social media posts about the COVID-19 vaccine:\n\n{context}\n\n"
        f"Based on this, would you take the COVID-19 vaccine? Answer Yes or No only."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def log_simulation(agent, label, method="manual"):
    new_row = pd.DataFrame([{ 
        "education": agent.education_level,
        "income": agent.socioeconomic_status,
        "belief": agent.prior_vaccine_belief,
        "age": agent.age_group,
        "personality": agent.personality,
        "response": label,
        "method": method
    }])
    if os.path.exists(log_path):
        new_row.to_csv(log_path, mode='a', header=False, index=False)
    else:
        new_row.to_csv(log_path, index=False)

# === SIMULATION TAB ===
with tab1:
    st.sidebar.header("🧬 Build Your Agent")
    age = st.sidebar.selectbox("Select Age Group", ["young adult", "middle-aged", "Old_aged"])
    edu = st.sidebar.selectbox("Select Education Level", ["no education", "high school", "bachelor", "master", "PhD"])
    inc = st.sidebar.selectbox("Select Income Level", ["low", "middle", "high"])
    bel = st.sidebar.selectbox("Select Vaccine Belief", ["anti-vaccine", "neutral", "pro-vaccine"])
    pers = st.sidebar.selectbox("Select Personality", ["anxious", "skeptical", "indifferent", "cautious", "open-minded"])

    agent = AgentProfile("Custom Agent", edu, pers, bel, inc, age)

    st.sidebar.header("🧪 Simulation Controls")
    tweet_count = st.sidebar.slider("🔢 Tweet Count", 5, 50, 10, step=5)
    real_pct = st.sidebar.slider("📰 % Real Tweets", 0, 100, 70, step=10)
    run = st.sidebar.button("🚀 Simulate")

    if run:
        df = load_tweets()
        real_sample = df[df.label == "real"].sample(int(tweet_count * real_pct / 100))
        fake_sample = df[df.label == "fake"].sample(tweet_count - len(real_sample))
        selected_tweets = pd.concat([real_sample, fake_sample]).sample(frac=1).reset_index(drop=True)
        context = "\n".join([f"- {row['tweet']}" for _, row in selected_tweets.iterrows()])
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
        pie_data = data["response"].value_counts().reset_index()
        pie_data.columns = ["Response", "Count"]
        st.plotly_chart(px.pie(pie_data, values='Count', names='Response', title='Vaccine Acceptance Distribution'))
        for col in ["education", "income", "belief", "age"]:
            bar_data = data.groupby(col)["response"].value_counts(normalize=True).unstack().fillna(0)
            if "Yes" in bar_data.columns:
                chart = px.bar(bar_data, y=bar_data.index, x="Yes", orientation='h', title=f"Acceptance Rate by {col.capitalize()}", labels={"Yes": "Acceptance Rate"})
                st.plotly_chart(chart, key=f"insight_chart_{col}")
    else:
        st.warning("No simulation data available yet.")

# === AUTO MODE TAB ===
with tab3:
    st.subheader("⚙️ Automated Simulation Mode")
    auto_start = st.button("▶ Start Auto Simulation")
    auto_stop = st.button("⏹ End and Show Insights")
    batch_size = st.slider("How many agents to simulate?", 10, 100, 50, step=10)
    tweet_count = st.slider("Tweets per agent", 5, 30, 10)
    real_pct = st.slider("% Real Tweets", 0, 100, 70, step=10)

    run_count = 0
    if os.path.exists(log_path):
        run_count = pd.read_csv(log_path).shape[0]
    st.markdown(f"### 🧮 Total Simulations Run: {run_count}")

    if auto_start:
        st.info("Running auto-simulations in background...")
        tweet_df = load_tweets()
        for _ in range(batch_size):
            agent = generate_random_agent()
            real_sample = tweet_df[tweet_df.label == "real"].sample(int(tweet_count * real_pct / 100))
            fake_sample = tweet_df[tweet_df.label == "fake"].sample(tweet_count - len(real_sample))
            selected_tweets = pd.concat([real_sample, fake_sample]).sample(frac=1).reset_index(drop=True)
            context = "\n".join([f"- {row['tweet']}" for _, row in selected_tweets.iterrows()])
            response = simulate_agent_final_response(agent, context)
            label = parse_binary_response(response)
            log_simulation(agent, label, method="auto")
        st.success(f"Auto-simulated {batch_size} agents!")

    if auto_stop:
        st.subheader("📊 Insights After Auto Run")
        if os.path.exists(log_path):
            data = pd.read_csv(log_path)
            pie_data = data["response"].value_counts().reset_index()
            pie_data.columns = ["Response", "Count"]
            st.plotly_chart(px.pie(pie_data, values='Count', names='Response', title='Vaccine Acceptance Among Agents'), key="auto_pie")
            for col in ["education", "income", "belief", "age"]:
                bar_data = data.groupby(col)["response"].value_counts(normalize=True).unstack().fillna(0)
                if "Yes" in bar_data.columns:
                    bar = px.bar(bar_data, y=bar_data.index, x="Yes", orientation='h', title=f"Acceptance Rate by {col.capitalize()}", labels={"Yes": "Acceptance Rate"})
                    st.plotly_chart(bar, key=f"auto_chart_{col}")
        else:
            st.warning("No simulation data available yet.")

# === FAKE VS REAL TAB ===
with tab4:
    st.subheader("📈 Effect of Real vs. Fake News on Vaccine Decision")
    st.markdown("Choose an agent and run repeated simulations while varying the % of real tweets.")

    col1, col2 = st.columns(2)
    with col1:
        age = st.selectbox("Age Group", ["young adult", "middle-aged", "Old_aged"])
        edu = st.selectbox("Education", ["no education", "high school", "bachelor", "master", "PhD"])
        inc = st.selectbox("Income", ["low", "middle", "high"])
    with col2:
        bel = st.selectbox("Belief", ["anti-vaccine", "neutral", "pro-vaccine"])
        pers = st.selectbox("Personality", ["anxious", "skeptical", "indifferent", "cautious", "open-minded"])
        n_runs = st.slider("Repeats per % real", 3, 20, 5)

    total_tweets = st.slider("Total Tweets per Run", 5, 50, 20)
    start = st.button("📊 Run Analysis")

    if start:
        fixed_agent = AgentProfile("FixedAgent", edu, pers, bel, inc, age)
        tweet_df = load_tweets()
        results = []

        for pct in range(0, 101, 10):
            yes_count = 0
            for _ in range(n_runs):
                real_sample = tweet_df[tweet_df.label == "real"].sample(int(total_tweets * pct / 100))
                fake_sample = tweet_df[tweet_df.label == "fake"].sample(total_tweets - len(real_sample))
                combined = pd.concat([real_sample, fake_sample]).sample(frac=1).reset_index(drop=True)
                context = "\n".join([f"- {row['tweet']}" for _, row in combined.iterrows()])
                with st.spinner(f"{pct}% real news, run {_ + 1}/{n_runs}..."):
                    reply = simulate_agent_final_response(fixed_agent, context)
                    label = parse_binary_response(reply)
                    if label == "Yes":
                        yes_count += 1
                    log_simulation(fixed_agent, label, method=f"real_pct_{pct}")
            results.append({"Real %": pct, "Acceptance Rate": yes_count / n_runs})

        plot_df = pd.DataFrame(results)
        line = px.line(plot_df, x="Real %", y="Acceptance Rate", markers=True, title="Acceptance Rate vs. % Real News")
        st.plotly_chart(line, use_container_width=True)

# === TEAM TAB ===
with tab5:
    st.markdown("""
    ### 👥 Team Members
    - Amir Pilehvarian (Lead Developer)
    - Partner 1 (Data Scientist)
    - Partner 2 (Public Health Analyst)
    - Partner 3 (LLM Engineering)

    ### 🧭 Project Goals
    - Simulate human-like responses to COVID-19 vaccine information
    - Explore how fake vs. real news impacts vaccine decisions
    - Build a secure, interactive simulation environment for health research
    """)

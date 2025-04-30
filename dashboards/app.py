# dashboards/app.py (Final Integrated Version)

import streamlit as st
import pandas as pd
import os
import re
from openai import OpenAI
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.data_utils import load_dataframe
from agents.agent_profiles import AgentProfile

st.set_page_config(page_title="💉 Vaccine Hesitancy Simulator", layout="wide")

client = OpenAI(api_key="***REMOVED***proj-PWzq-G9ROlKwUyUuyNSScDj9wkucQo3kBNplhNs1E-C-yqzLL534T_8fRJKFwNpk-SIXycScqTT3BlbkFJ2UvedUdXHOd79KzN_BRh5CgQHW7Ke2cueooufmmrL4oxuQY2I5E3IhgMbUQXFoSCgwvn1Yvg4A")

# === Trait Options ===
education_levels = ["no education", "high school", "bachelor's", "master's", "PhD"]
personalities = ["anxious", "skeptical", "indifferent", "cautious", "open-minded"]
incomes = ["low", "middle", "high"]
beliefs = ["anti-vaccine", "neutral", "pro-vaccine"]
age_groups = ["young adult", "middle-aged", "senior"]

# === Styling ===
st.markdown("""
    <style>
        html, body, [class*="css"] {
            background-color: white !important;
        }
        .header {
            font-size: 36px !important;
            font-weight: 700;
            color: #2c6df3;
        }
        .subhead {
            font-size: 24px !important;
            font-weight: 600;
            color: #444;
            margin-top: 20px;
        }
        .agent-answer {
            font-size: 18px;
            padding: 1rem 0;
            margin-top: 1rem;
            line-height: 1.6;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>💉 Vaccine Hesitancy Simulator</div>", unsafe_allow_html=True)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
st.sidebar.header("🧬 Build Your Agent")

# === Agent Profile Selector ===
age = st.sidebar.selectbox("Select Age Group", age_groups)
edu = st.sidebar.selectbox("Select Education Level", education_levels)
inc = st.sidebar.selectbox("Select Income Level", incomes)
bel = st.sidebar.selectbox("Select Vaccine Belief", beliefs)
pers = st.sidebar.selectbox("Select Personality", personalities)

agent = AgentProfile(
    name="Custom Agent",
    age_group=age,
    education_level=edu,
    socioeconomic_status=inc,
    prior_vaccine_belief=bel,
    personality=pers
)

# === Simulation Parameters ===
st.sidebar.header("🧪 Simulation Controls")
tweet_count = st.sidebar.slider("🔢 Tweet Count", 0, 500, 50, step=5)
real_pct = st.sidebar.slider("📰 % Real Tweets", 0, 100, 70, step=10)
run = st.sidebar.button("🚀 Simulate")

# === Simulation Runner ===
@st.cache_data
def load_tweets():
    return load_dataframe("tweets.csv")

def simulate_agent_final_response(agent: AgentProfile, context: str) -> str:
    system_prompt = (
        f"You are simulating a person who is {agent.age_group}, {agent.personality}, has {agent.education_level} education, "
        f"is from a {agent.socioeconomic_status} background, and initially is '{agent.prior_vaccine_belief}' about vaccines."
    )
    user_prompt = (
        f"Here are a number of social media posts about the COVID-19 vaccine:\n\n{context}\n\n"
        f"Based on this, would you take the COVID-19 vaccine? Answer with Yes or NO only"
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

if run:
    df = load_tweets()
    real_sample = df[df.label == "real"].sample(int(tweet_count * real_pct / 100))
    fake_sample = df[df.label == "fake"].sample(tweet_count - len(real_sample))
    selected_tweets = pd.concat([real_sample, fake_sample]).sample(frac=1).reset_index(drop=True)

    # Create context
    context = "\n".join([f"- {row['tweet']}" for _, row in selected_tweets.iterrows()])

    st.markdown("<div class='subhead'>🧠 Final Agent Response</div>", unsafe_allow_html=True)
    with st.spinner("Thinking like your agent..."):
        final_response = simulate_agent_final_response(agent, context)
        st.markdown(f"<div class='agent-answer'>{final_response}</div>", unsafe_allow_html=True)

# simulation/run_simulation.py

import random
from openai import OpenAI
from agents.agent_profiles import generate_agent_list
import pandas as pd

# Load your OpenAI key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def simulate_agent_response(agent, news_text):
    """Use GPT to simulate an agent's vaccine response."""
    system_prompt = (
        f"You are simulating a person who is {agent.age_group}, {agent.personality}, has {agent.education_level} education, "
        f"is from a {agent.socioeconomic_status} background, and initially is '{agent.prior_vaccine_belief}' about vaccines."
    )

    user_prompt = (
        f"Based on this news article:\n\n{news_text}\n\n"
        f"Would you take the COVID-19 vaccine after reading this? Please answer Yes or No and explain in one sentence."
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


def run_simulation(news_df, n_agents=3, n_articles=3):
    agents = generate_agent_list(n_agents)
    subset = news_df.sample(n=min(n_articles, len(news_df)))
    records = []

    for agent in agents:
        for _, row in subset.iterrows():
            result = simulate_agent_response(agent, row['text'])
            records.append({
                "agent": agent.name,
                "profile": agent.describe(),
                "news_title": row.get('title', 'N/A'),
                "source": row.get('source', 'unknown'),
                "response": result
            })

    return pd.DataFrame(records)

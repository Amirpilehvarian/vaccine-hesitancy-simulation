# 💉 Vaccine Hesitancy Simulation & Persuasive Agent

An interactive Streamlit-based platform to explore how different types of information, public messaging, and agent profiles affect COVID-19 vaccine acceptance. This project uses synthetic agents powered by large language models (LLMs) to simulate decision-making and test communication strategies for combating misinformation.

---

## 📚 Dataset Description

This project uses the **COVID-19 Fake News Detection** dataset from the [CONSTRAINT-2021 shared task](https://competitions.codalab.org/competitions/26655). The dataset consists of English-language social media posts (from Twitter, Facebook, Instagram) labeled as either `real` or `fake`.

- Kaggle Source: [COVID19 Tweet Truth Analysis](https://www.kaggle.com/code/lunamcbride24/covid19-tweet-truth-analysis/notebook)  
- GitHub Repository: [diptamath/covid_fake_news](https://github.com/diptamath/covid_fake_news)  
- Reference Paper: [Das et al., 2021](https://arxiv.org/abs/2101.03545)

---

## 🧠 Project Structure
vaccine-hesitancy-simulation/
├── dashboards/
│   └── app.py                 # Main Streamlit app
├── agents/
│   └── agent_profiles.py      # Agent profile generator
├── utils/
│   └── data_utils.py          # Tweet loader & scraping utilities
├── data/
│   ├── simulation_log.csv     # Logs for manual & auto simulation
│   ├── fake_vs_real_log.csv   # Logs for fake-vs-real experiments
│   ├── emotion_celebrity_log.csv  # Logs for messaging strategy tab
├── .env                       # OpenAI API key
└── README.md

---

## 🧬 Agent Design

Each agent has attributes such as:
- Age group (young adult, middle-aged, senior)
- Education level (no education → PhD)
- Income level (low → high)
- Personality (anxious, skeptical, indifferent, cautious, open-minded)
- Prior vaccine belief (anti-vaccine, neutral, pro-vaccine)

Agents are exposed to different tweet streams and asked if they would take the vaccine after reading.

---

## 🚀 Features

### Tabs:
- **Simulation**: Manually configure and test an agent’s response to vaccine-related content  
- **Insights**: Visualize aggregate vaccine acceptance trends by profile  
- **Auto Mode**: Batch simulate random agents to uncover global trends  
- **Fake vs Real**: Measure the impact of tweet content mix on vaccine willingness  
- **Emotion & Celebrity**: Test persuasive messaging strategies  
- **Persuasive Chatbot**: Empathetic LLM chatbot that adapts to user profile to build trust and encourage vaccination  
- **Team**: Project members and goals

---

## 📈 Key Findings

- Vaccine acceptance increases with **education**, **income**, and **exposure to factual information**
- **Young adults** are most receptive, followed by middle-aged and seniors
- **Emotional appeals** and **celebrity messages** improve persuasion in low-trust groups
- Personalized, empathetic messaging consistently outperforms generic information

---

## ⚖️ Ethics

This is a simulation framework using synthetic agents. No real user data is collected or inferred. The purpose is to explore ethical and effective health communication strategies, not to manipulate.

---

## 🔑 Setup & Run

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/vaccine-hesitancy-simulation.git
   cd vaccine-hesitancy-simulation
   
   
   
@article{das2021heuristic,
  title={A Heuristic-driven Ensemble Framework for COVID-19 Fake News Detection},
  author={Das, Sourya Dipta and Basak, Ayan and Dutta, Saikat},
  journal={arXiv preprint arXiv:2101.03545},
  year={2021}
}
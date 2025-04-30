# agents/agent_profiles.py

import random
from dataclasses import dataclass

@dataclass
class AgentProfile:
    name: str
    education_level: str
    personality: str
    prior_vaccine_belief: str
    socioeconomic_status: str
    age_group: str

    def describe(self):
        return (f"{self.name}, a {self.age_group} individual with {self.education_level} education, "
                f"has a {self.personality} personality, a {self.socioeconomic_status} background, "
                f"and initially holds a '{self.prior_vaccine_belief}' view about vaccines.")


EDUCATION_LEVELS = ["high school", "college", "bachelor's degree", "master's degree", "PhD"]
PERSONALITIES = ["skeptical", "open-minded", "anxious", "indifferent", "cautious"]
VACCINE_BELIEFS = ["pro-vaccine", "neutral", "anti-vaccine"]
SOCIO_STATUSES = ["low-income", "middle-income", "high-income"]
AGE_GROUPS = ["young adult", "middle-aged", "senior"]


def generate_random_agent(name="Agent X"):
    return AgentProfile(
        name=name,
        education_level=random.choice(EDUCATION_LEVELS),
        personality=random.choice(PERSONALITIES),
        prior_vaccine_belief=random.choice(VACCINE_BELIEFS),
        socioeconomic_status=random.choice(SOCIO_STATUSES),
        age_group=random.choice(AGE_GROUPS)
    )


def generate_agent_list(n):
    return [generate_random_agent(f"Agent {i+1}") for i in range(n)]

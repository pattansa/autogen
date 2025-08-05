
import os
import random
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
import os
from act_reading import READING_TUTOR_SYSTEM_MESSAGE, READING_FEEDBACK_SYSTEM_MESSAGE

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
model_client = OpenAIChatCompletionClient(model='gpt-4o', api_key=api_key)

# --- User Input ---
#subject = input("Please enter the section for which you are preparing(e.g., 'Math', 'Reading'): ")
print(f"\nGreat! Starting an interview simulation for a reading section.\n")
# --- Agent Definitions ---

# 1. Interviewer Agent
interviewer = AssistantAgent(
    name="Interviewer",
    system_message=READING_TUTOR_SYSTEM_MESSAGE,
    model_client=model_client
)

# 2. Career Coach Agent
career_coach = AssistantAgent(
    name="Career_Coach",
    system_message=READING_FEEDBACK_SYSTEM_MESSAGE,
    model_client=model_client
)

# 3. Applicant Agent
applicant = UserProxyAgent(
    name="Applicant",
    input_func=input
)


terminate_condition=TextMentionTermination(text="TERMINATE")

# The order of agents in this list determines the round-robin sequence.
# The flow will be: Applicant (initiates) -> Interviewer -> Career_Coach -> Applicant -> ...
team = RoundRobinGroupChat(
    participants=[ interviewer,applicant, career_coach],
    termination_condition=terminate_condition,
    max_turns=31, # 10 questions = 10 * (answer + question + advice) = 30 rounds + 1 initial message
)

async def interview():
    async for message in team.run_stream(task='Start the interview with the first question ?'):
        if isinstance(message, TextMessage):
            message = message.content
            yield message
        elif isinstance(message, TaskResult):
            yield message.output

async def run_team():
    async for message in interview():
        print("-"*50)
        print(message)

if (__name__ == "__main__"):
    asyncio.run(run_team())
    print("\n--- Interview Simulation Finished ---")

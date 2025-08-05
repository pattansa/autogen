
import os
import random
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
model_client = OpenAIChatCompletionClient(model='gpt-4o', api_key=api_key)

# --- User Input ---
job_position = input("Please enter the job position you are interviewing for (e.g., 'Software Engineer', 'Product Manager'): ")
print(f"\nGreat! Starting an interview simulation for a '{job_position}' role.\n")
# --- Agent Definitions ---

# 1. Interviewer Agent
interviewer = AssistantAgent(
    name="Interviewer",
    system_message=f"""You are a strict but fair hiring manager.
Your role is to interview a candidate for a '{job_position}' position.
Ask exactly one insightful, relevant question at a time.
Do not ask for introductions or engage in small talk. Start with the first question.
Do not say "Thank you" or "That's all". Answer the next question after the career coach provide his observation.
When the conversation is over, simply say 'TERMINATE'.""",
    model_client=model_client
)

# 2. Career Coach Agent
career_coach = AssistantAgent(
    name="Career_Coach",
    system_message=f"""You are a helpful career coach.
Your role is to listen to the question asked by the Interviewer and answer provided by the applicant. Wait for the applicant to answer before providing a brief, constructive tip to the Applicant on how to best answer it.
You should suggest a structure or key points to cover.
Address your advice directly to the Applicant. Do not answer the question yourself.
Keep your advice concise (2-3 sentences).""",
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

async def interview(job_position):
    async for message in team.run_stream(task='Start the interview with the first question ?'):
        message = message.content
        yield message

async def run_team():
    async for message in interview(job_position):
        print("-"*50)
        print(message)

if (__name__ == "__main__"):
    asyncio.run(run_team())
    print("\n--- Interview Simulation Finished ---")

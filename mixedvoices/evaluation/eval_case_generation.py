from typing import List

from openai import OpenAI

client = OpenAI()

system_prompt_dict = {
    "role": "system",
    "content": "You're an expert at creating prompts for "
    "TESTING agents to test against REAL agents. "
    "GOAL: Create TESTING prompts that simulate real world scenarios. "
    "Don't create a conversation, just the prompt. "
    "Don't give the agent an exact script."
    "Don't evaluate the conversation or any behaviour. "
    "Give the TESTING agent a name along with age and personality."
    "Ensure that each prompt follows a structured outline for the TESTING agent to follow. "
    "Ensure that the bot always finishes conversation and says goodbye"
    "This will be a text conversation only, "
    "so voice speed/modulation, background noise etc. won't matter. "
    "Ensure that the TESTING agent won't go in loops and repeats."
    "Adversarial prompts could start with 'You are a'",
}

output_prompt_dict = {"role": "assistant", "content": "Output:"}

common_prompt = """Try to make the prompts distinct.
Return output as a {count} strings separated by ---- (4 dashes) without numbering

Example:
First prompt
----
Second prompt
----
Third prompt
----
and so on"""


def generate_eval_prompts_for_failure_reasons(
    agent_prompt: str,
    failure_reasons: List[str],
    count: int = 2,
):
    eval_prompts = []
    model = "gpt-4o"
    end_prompt = common_prompt.format(count=count)
    for failure_reason in failure_reasons:
        prompt = f"""REAL agent prompt:
----
{agent_prompt}
----
Generate {count} different TESTING agent prompts that try to recreate this failure: {failure_reason}
{end_prompt}"""  # noqa: E501
        completion = client.chat.completions.create(
            model=model,
            messages=[
                system_prompt_dict,
                {"role": "user", "content": prompt},
                output_prompt_dict,
            ],
        )
        response_text = completion.choices[0].message.content
        prompts = response_text.split("----")
        prompts = [p for p in prompts if len(p) > 50]
        eval_prompts.extend(prompts)

    return eval_prompts


def generate_eval_prompts_for_new_paths(
    agent_prompt: str,
    new_paths: List[str],
    count: int = 2,
):
    eval_prompts = []
    model = "gpt-4o"
    for new_path in new_paths:
        end_prompt = common_prompt.format(count=count)
        prompt = f"""REAL agent prompt:
----
{agent_prompt}
----
Generate {count} different TESTING agent prompts that follow this path: {new_path}
{end_prompt}
"""
        completion = client.chat.completions.create(
            model=model,
            messages=[
                system_prompt_dict,
                {"role": "user", "content": prompt},
                output_prompt_dict,
            ],
        )
        response_text = completion.choices[0].message.content
        prompts = response_text.split("----")
        prompts = [p for p in prompts if len(p) > 50]
        eval_prompts.extend(prompts)

    return eval_prompts


def generate_eval_prompts_for_edge_cases(agent_prompt: str, count: int = 2):
    model = "gpt-4o"
    end_prompt = common_prompt.format(count=count)
    prompt = f"""REAL agent prompt:
----
{agent_prompt}
----
Generate {count} different TESTING agent prompts to simulate tricky edge cases.
{end_prompt}"""

    completion = client.chat.completions.create(
        model=model,
        messages=[
            system_prompt_dict,
            {"role": "user", "content": prompt},
            output_prompt_dict,
        ],
    )
    response_text = completion.choices[0].message.content
    prompts = response_text.split("----")
    prompts = [p for p in prompts if len(p) > 50]
    return prompts


def generate_eval_prompts(
    agent_prompt: str,
    failure_reasons: List[str],
    new_paths: List[str],
):
    failure_reasons = []
    new_paths = [
        "Greeting->Inquiry Handling->Set Appointment->Farewell",
        "Greeting->Caller Complaint Handling->Farewell",
    ]
    # TODO: remove hard coded values and counts
    testcases_per_path = 1
    testcases_per_failure_reason = 1
    testcases_for_edge_cases = 1
    new_path_prompts = generate_eval_prompts_for_new_paths(
        agent_prompt, new_paths, testcases_per_path
    )
    failure_prompts = generate_eval_prompts_for_failure_reasons(
        agent_prompt, failure_reasons, testcases_per_failure_reason
    )
    edge_case_prompts = generate_eval_prompts_for_edge_cases(
        agent_prompt, testcases_for_edge_cases
    )
    return new_path_prompts + failure_prompts + edge_case_prompts


if __name__ == "__main__":
    agent_prompt = """You are a voice assistant for Locoto's Dental, a dental office located at 123 North Face Place, Anaheim, California. The hours are 8 AM to 5PM daily, but they are closed on Sundays.

    Locoto's dental provides dental services to the local Anaheim community. The practicing dentist is Dr. Mary Smith.

    You are tasked with answering questions about the business, and booking appointments. If they wish to book an appointment, your goal is to gather necessary information from callers in a friendly and efficient manner like follows:

    1. Ask for their full name.
    2. Ask for the purpose of their appointment.
    3. Request their preferred date and time for the appointment.
    4. Confirm all details with the caller, including the date and time of the appointment.

    - Be sure to be kind of funny and witty!
    - Keep all your responses short and simple. Use casual language, phrases like "Umm...", "Well...", and "I mean" are preferred.
    - This is a voice conversation, so keep your responses short, like in a real conversation. Don't ramble for too long.
    """

    new_paths = [
        "Greeting->Determine Call Purpose->Provide Business Information->Farewell"
    ]
    failure_reasons = ["Bot doesn't know what day/time it is currently"]

    eval_prompts = generate_eval_prompts(agent_prompt, failure_reasons, new_paths)

    for i, prompt in enumerate(eval_prompts):
        print(f"Prompt {i}: {prompt}")
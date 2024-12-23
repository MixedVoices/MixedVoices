from typing import Tuple

from agent import DentalAssistant

import mixedvoices as mv
from mixedvoices import BaseAgent


def check_conversation_ended(assistant_message):
    return (
        "bye" in assistant_message.lower()
        or "see you" in assistant_message.lower()
        or "see ya" in assistant_message.lower()
        or "catch you" in assistant_message.lower()
        or "talk to you" in assistant_message.lower()
    )


class DentalAgent(BaseAgent):
    def __init__(self):
        self.assistant = DentalAssistant(mode="text")

    def respond(self, input_text: str) -> Tuple[str, bool]:
        response = self.assistant.get_assistant_response(input_text)
        has_conversation_ended = check_conversation_ended(response)
        return response, has_conversation_ended

    @property
    def starts_conversation(self):
        return None


project = mv.load_project("dental_clinic")
version = project.load_version("v1")
evaluator = version.create_evaluator(1, 1, 1)
evaluator.run(DentalAgent)

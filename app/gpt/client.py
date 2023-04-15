from dataclasses import dataclass, field
import os
from typing import List

import openai
from openai.openai_object import OpenAIObject

from .constants import Model
from .message import Message

@dataclass
class ChatGPTClient:
    model: Model
    messages: List[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (key := os.getenv("OPENAI_API_KEY")):
            raise Exception(
                "ChatGPT api key is not set as an environment variable"
            )
        openai.api_key = key

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def create(self) -> OpenAIObject:
        res = openai.ChatCompletion.create(
            model=self.model.value,
            messages=[m.to_dict() for m in self.messages],
        )
        self.add_message(Message.from_dict(res["choices"][0]["message"]))
        return res
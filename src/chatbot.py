"""
This is the processing code that process and prepares the data for ingestion into the model

Author: Martin Hatting Petersen
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class Chatbot:
    def __init__(self, config):
        self._model_name = config.model.get(
            "pretrained_model", "microsoft/DialoGPT-medium"
        )
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
        self._model = AutoModelForCausalLM.from_pretrained(self._model_name)
        self._response_max_length = config.model.get("response_max_length", 1000)
        self._chat_history_ids = None
        self._chat_history = []
        self._history_size = config.model.get("history_size", 100)

    # encode text into ids
    def encode(self, text):
        return self._tokenizer.encode(
            text + self._tokenizer.eos_token, return_tensors="pt"
        )

    # decode ids into text
    def decode(self, input_ids):
        return self._tokenizer.decode(input_ids, skip_special_tokens=True)

    # generate response to input text
    def __call__(self, text):
        # only keep last self._history_size number of samples
        if len(self._chat_history) > self._history_size:
            # find the eos token that splits on the history to keep
            limiter = (self._chat_history_ids == self._tokenizer.eos_token_id).nonzero(
                as_tuple=False
            )[-(self._history_size * 2 + 1), 1].item() + 1
            # remove history outside window
            self._chat_history_ids = self._chat_history_ids[:, limiter:]
            # remove history outside window
            self._chat_history = self._chat_history[-self._history_size :]
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        user_input_ids = self.encode(text)
        # append the new user input tokens to the chat history
        input_ids = (
            torch.cat([self._chat_history_ids, user_input_ids], dim=-1)
            if self._chat_history_ids is not None
            else user_input_ids
        )
        input_length = input_ids.shape[-1]
        # generated a response while limiting the total chat history to 1000 tokens
        self._chat_history_ids = self._model.generate(
            input_ids,
            max_length=self._response_max_length,
            pad_token_id=self._tokenizer.eos_token_id,
        )
        # return last ouput tokens from bot
        response = self.decode(self._chat_history_ids[:, input_length:][0])
        # store dict of input and output text
        self._chat_history.append({"User": text, "Bot": response})
        return response

    def __repr__(self):
        return f"{self.__class__.__qualname__}(model_name = {self._model_name})"

    def print_conversation(self):
        for d in self._chat_history:
            print(f"User --> {d['User']}")
            print(f"Bot  --> {d['Bot']}")

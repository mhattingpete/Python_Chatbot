"""
This is the processing code that process and prepares the data for ingestion into the model

Author: Martin Hatting Petersen
"""

import transformers as trs

from utils import get_model_attr


class ChatbotBase:
    def __init__(self, config, model_type, **model_kwargs):
        self._model_name = get_model_attr(
            config, "pretrained_model", "microsoft/DialoGPT-medium"
        )
        self._response_max_length = get_model_attr(config, "response_max_length", 1000)
        self._tokenizer = getattr(trs, "AutoTokenizer").from_pretrained(
            self._model_name
        )
        self._model = getattr(trs, model_type, "AutoModel").from_pretrained(
            self._model_name, **model_kwargs
        )

    # encode text into ids
    def encode(self, *args, **kwargs):
        return self._tokenizer(*args, **kwargs, return_tensors="pt")
        """
        try:
            code above
        except:
            return self._tokenizer.encode(
                *args, **kwargs, return_tensors="pt"
            )
        """

    # decode ids into text
    def decode(self, input_ids, **kwargs):
        return self._tokenizer.decode(input_ids, **kwargs)

    def generate(self, input_ids, **kwargs):
        return self._model.generate(input_ids, **kwargs)

    def model_call(self, inputs):
        return self._model(**inputs)

    def __repr__(self):
        return f"{self.__class__.__qualname__}(model_name = '{self._model_name})'"

    # generate response to input text
    def __call__(self, text):
        # encode text
        inputs = self.encode(text)
        # generate response
        generated = self.generate(
            inputs["input_ids"], max_new_tokens=self._response_max_length
        )
        # decode output
        output = self.decode(generated, skip_special_tokens=True)
        return output

"""
This is the processing code that process and prepares the data for ingestion into the model

Author: Martin Hatting Petersen
"""

import transformers as trs

from basemodel import ChatbotBase
from utils import argmax, concat_if_set, get_model_attr


class DialogChatbot(ChatbotBase):
    def __init__(self, config):
        model_type = "AutoModelForCausalLM"
        super().__init__(config, model_type, device_map="auto", torch_dtype="auto")
        self._chat_history_ids = None

    # encode the raw text input
    def encode(self, text):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        user_input_ids = super().encode(text + self._tokenizer.eos_token)
        # append the new user input tokens to the chat history
        input_ids = concat_if_set(self._chat_history_ids, user_input_ids)
        return input_ids

    # generate a response to the given input
    def generate(self, input_ids):
        input_length = input_ids.shape[-1]
        # generated a response while limiting the total chat history to 1000 tokens
        self._chat_history_ids = super().generate(
            input_ids,
            max_new_tokens=self._response_max_length,
            pad_token_id=self._tokenizer.eos_token_id,
        )
        # return last ouput tokens from bot
        response = self.decode(
            self._chat_history_ids[:, input_length:][0], skip_special_tokens=True
        )
        return response

    # generate response to input text
    def __call__(self, text):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        input_ids = self.encode(text)
        # generate a response
        response = self.generate(input_ids)
        return response


class RetrievalChatbot(ChatbotBase):
    def __init__(self, config):
        raise NotImplementedError
        model_type = "RagSequenceForGeneration"
        index_name = get_model_attr(config, "index_name", "exact")
        use_dummy_dataset = get_model_attr(config, "use_dummy_dataset", True)
        self._retriever = trs.RagRetriever.from_pretrained(
            self._get_model_name(config),
            index_name=index_name,
            use_dummy_dataset=use_dummy_dataset,
        )
        super().__init__(
            config,
            model_type,
            use_dummy_dataset=use_dummy_dataset,
            retriever=self._retriever,
        )


class QAChatbot(ChatbotBase):
    def __init__(self, config):
        model_type = "AutoModelForQuestionAnswering"
        super().__init__(config, model_type)
        self.context = """
        Srinivasa Ramanujan born Srinivasa Ramanujan Aiyangar, 22 December 1887 - 26 April 1920 was an Indian mathematician who lived during British Rule in India.
        Though he had almost no formal training in pure mathematics, he made substantial contributions to mathematical analysis, number theory, infinite series, and continued fractions,
        including solutions to mathematical problems then considered unsolvable. Ramanujan initially developed his own mathematical research in isolation:
        according to Hans Eysenck: "He tried to interest the leading professional mathematicians in his work, but failed for the most part. What he had to show them was too novel,
        too unfamiliar, and additionally presented in unusual ways; they could not be bothered". Seeking mathematicians who could better understand his work,
        in 1913 he began a postal correspondence with the English mathematician G. H. Hardy at the University of Cambridge, England. Recognising Ramanujan's work as extraordinary,
        Hardy arranged for him to travel to Cambridge. In his notes, Hardy commented that Ramanujan had produced groundbreaking new theorems,
        including some that "defeated me completely; I had never seen anything in the least like them before", and some recently proven but highly advanced results.
        """

    def extract_answer_span(self, start_logits, end_logits):
        # Get the most likely beginning of answer with the argmax of the score
        answer_start = argmax(start_logits)
        # Get the most likely end of answer with the argmax of the score
        answer_end = argmax(end_logits) + 1
        return answer_start, answer_end

    def extract_answer(self, inputs, outputs):
        # get context for answer extraction
        input_ids = inputs["input_ids"].tolist()[0]
        # get answer span
        answer_start, answer_end = self.extract_answer_span(
            outputs.start_logits, outputs.end_logits
        )
        # return answer ids
        return input_ids[answer_start:answer_end]

    # generate response to input question
    def __call__(self, question):
        # encode question and context
        inputs = self.encode(question, self.context, add_special_tokens=True)
        # get output
        outputs = self.model_call(inputs)
        # get answer
        answer_ids = self.extract_answer(inputs, outputs)
        return self.decode(answer_ids, skip_special_tokens=False)


if __name__ == "__main__":
    from hydra import compose, initialize

    with initialize(version_base=None, config_path="../config", job_name="chatbot_app"):
        config = compose(config_name="main")
        bot = QAChatbot(config)
    test = "When did Ramanujan die?"
    print(bot(test))
    test = "What is Ramanujan's birth name?"
    print(bot(test))

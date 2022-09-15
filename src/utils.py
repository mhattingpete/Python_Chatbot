"""
This is the processing code that process and prepares the data for ingestion into the model

Author: Martin Hatting Petersen
"""

import torch
from hydra import compose, initialize


def _concat_tensors(tensor1, tensor2, dim=-1):
    return torch.cat([tensor1, tensor2], dim=dim)


def concat_if_set(tensor1, tensor2):
    return _concat_tensors(tensor1, tensor2) if tensor1 is not None else tensor2


def argmax(tensor1):
    return torch.argmax(tensor1)


def get_model_attr(config, attr_name, default_value):
    return config.model.get(attr_name, default_value)


def load_config(config_path="../config", config_name="main"):
    with initialize(version_base=None, config_path=config_path, job_name="chatbot_app"):
        config = compose(config_name=config_name)
        return config

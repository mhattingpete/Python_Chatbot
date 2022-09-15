import logging

from flask import Flask, render_template, request

import models
from utils import get_model_attr, load_config

app = Flask(__name__)

# set logging format
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_bot():
    logger.info("Initializing chatbot")
    # context initialization
    config = load_config(config_path="../config", config_name="main")
    botcls = getattr(models, get_model_attr(config, "type", "DialogChatbot"))
    bot = botcls(config)
    logger.info(f"{bot} initialized")
    return bot


bot = get_bot()


def main():
    app.run(debug=True, use_reloader=False)


@app.route("/")
def home():
    logger.info("Rendering start page")
    return render_template("index.html")


@app.route("/get_response", methods=["POST", "GET"])
def get_bot_response():
    logger.info("Parsing request")
    try:
        if request.method == "POST":
            text = request.get_json()["msg"]

        else:
            text = request.args.get("msg")
    except Exception as err:
        logger.error(err)
    logger.debug(f"Calling chatbot with input: {text}")
    return str(bot(text))


if __name__ == "__main__":
    main()

import logging

from flask import Flask, render_template, request
from hydra import compose, initialize

from chatbot import Chatbot

app = Flask(__name__)

# set logging format
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_bot():
    logger.info("Initializing chatbot")
    # context initialization
    with initialize(version_base=None, config_path="../config", job_name="chatbot_app"):
        config = compose(config_name="main")
        bot = Chatbot(config)
        logger.info("Chatbot initialized")
    return bot


bot = get_bot()


def main():
    app.run(debug=True)


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

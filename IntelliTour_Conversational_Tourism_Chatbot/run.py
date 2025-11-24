import logging

from app import create_app
from dotenv import load_dotenv
load_dotenv()

app = create_app()



if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=5000)

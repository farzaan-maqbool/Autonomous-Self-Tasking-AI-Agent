"""Launcher file so the project can be started with `python app.py`."""

from agent.app import app


# if __name__ == "__main__":
#     app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
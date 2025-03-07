from application import app  # noqa: INP001
from application.common.console_io import clear_scr

if __name__ == "__main__":
    clear_scr()
    app.run()

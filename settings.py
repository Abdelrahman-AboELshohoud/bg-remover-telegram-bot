import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "./temp"))
    PROCESSED_DIR: Path = Path(os.getenv("PROCESSED_DIR", "./processed"))
    CLEANUP_AFTER_SEND: bool = os.getenv("CLEANUP_AFTER_SEND", "1") == "1"
    TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "30"))

    @classmethod
    def prepare_dirs(cls) -> None:
        cls.TEMP_DIR.mkdir(exist_ok=True, parents=True)
        cls.PROCESSED_DIR.mkdir(exist_ok=True, parents=True)
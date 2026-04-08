from bot import ShinyMacroBot
from config import load_config


def main() -> None:
    config = load_config("settings.json")
    bot = ShinyMacroBot(config)
    bot.run()


if __name__ == "__main__":
    main()
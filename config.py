import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class BotConfig:
    esp_host: str
    esp_port: int

    cap_index: int

    roi_claiming: tuple[int, int, int, int]
    roi_rival: tuple[int, int, int, int]
    roi_shiny: tuple[int, int, int, int]

    tpl_claiming: Path
    tpl_rival: Path

    th_claiming: float
    th_rival: float
    rival_hit_cooldown: float

    spam_period: float
    tap_press: float
    after_seq_wait: float
    check_cooldown: float

    yellow_th: float
    yellow_lower: tuple[int, int, int]
    yellow_upper: tuple[int, int, int]
    black_mean_th: float

    debug_dir: Path
    manual_capture_dir: Path
    full_dir: Path

    main_window: str


class State(str, Enum):
    SPAM_A = "SPAM_A"
    SPAM_B = "SPAM_B"
    RIVAL_SEQ = "RIVAL_SEQ"
    CHECK_SHINY = "CHECK_SHINY"
    SHINY_WAIT = "SHINY_WAIT"


def _to_tuple4(values) -> tuple[int, int, int, int]:
    if len(values) != 4:
        raise ValueError(f"expected 4 values, got {len(values)}: {values}")
    return tuple(values)


def _to_tuple3(values) -> tuple[int, int, int]:
    if len(values) != 3:
        raise ValueError(f"expected 3 values, got {len(values)}: {values}")
    return tuple(values)


def resolve_path(path_str: str) -> Path:
    return (BASE_DIR / path_str).resolve()


def load_config(config_path: str = "settings.json") -> BotConfig:
    path = resolve_path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    return BotConfig(
        esp_host=raw["esp_host"],
        esp_port=raw["esp_port"],
        cap_index=raw["cap_index"],

        roi_claiming=_to_tuple4(raw["roi_claiming"]),
        roi_rival=_to_tuple4(raw["roi_rival"]),
        roi_shiny=_to_tuple4(raw["roi_shiny"]),

        tpl_claiming=resolve_path(raw["tpl_claiming"]),
        tpl_rival=resolve_path(raw["tpl_rival"]),

        th_claiming=raw["th_claiming"],
        th_rival=raw["th_rival"],
        rival_hit_cooldown=raw["rival_hit_cooldown"],

        spam_period=raw["spam_period"],
        tap_press=raw["tap_press"],
        after_seq_wait=raw["after_seq_wait"],
        check_cooldown=raw["check_cooldown"],

        yellow_th=raw["yellow_th"],
        yellow_lower=_to_tuple3(raw["yellow_lower"]),
        yellow_upper=_to_tuple3(raw["yellow_upper"]),
        black_mean_th=raw["black_mean_th"],

        debug_dir=resolve_path(raw["debug_dir"]),
        manual_capture_dir=resolve_path(raw["manual_capture_dir"]),
        full_dir=resolve_path(raw["full_dir"]),

        main_window=raw["main_window"],
    )
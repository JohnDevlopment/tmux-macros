#!/usr/bin/env -S python3 -O
"""
tmux-macros: A tool to run macros in tmux using Python scripts.
This script allows you to run predefined macros in tmux panes.
It reads macros from a YAML file, generates a cache, and allows execution of macros via command line arguments.
"""

import argparse
import os
import subprocess
from pathlib import Path
from time import sleep
from typing import Any

from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Success

from my_typings import StrPath
from utils import is_what, load_conf, parse_macros_yml_and_generate_cache, tmux_print


def get_target():
    return subprocess.check_output(
        ["tmux", "display-message", "-p", "#{session_id}:#{window_id}.#{pane_id}"],
        text=True
    ).strip()


def send_command_to_target(target, command):
    subprocess.run(["tmux", "send-keys", "-t", target, command])


def run_macro(macros_dict, macro_name):
    tmux_print(f"Running macro: {macro_name}")
    target = get_target()
    if macro_name not in macros_dict:
        tmux_print(f"Macro '{macro_name}' not found.")
        return

    for c in macros_dict[macro_name]["commands"]:
        if c["type"] == "text" or c["type"] == "keypress":
            send_command_to_target(target, c["value"])
        elif c["type"] == "sleep":
            sleep(0.001 * int(c["value"]))


def load_cache(location: StrPath) -> Maybe[dict[str, Any]]:
    import pickle

    with open(location, "rb") as fd:
        macros_dict = pickle.load(fd)
        if not is_what(macros_dict, dict, dict[str, "Any"]):
            raise ValueError(f"pickled data is not a dict but a {type(macros_dict)}")

    return Some(macros_dict)


def main() -> int:
    def _args():
        parser = argparse.ArgumentParser()
        parser.add_argument("macro", nargs="?", help="Macro to execute")
        parser.add_argument(
            "--update-cache",
            action="store_true",
            help="Regenerate macros_cache.py and .tmux.macros.conf",
        )
        parser.add_argument(
            "--config",
            "-c",
            type=Path,
            metavar="FILE",
            help="Use FILE as the config file",
        )
        parser.add_argument(
            "--plugin-dir",
            type=Path,
            metavar="DIR",
            help="load plugin files from DIR",
        )
        return parser.parse_args()
    args = _args()

    # Load config file
    config_file: Maybe[Path] = Maybe.from_value(args.config)
    plugin_dir: Maybe[Path] = Maybe.from_value(args.plugin_dir)
    conf: dict[str, str] = {}
    match load_conf(config_file, plugin_dir):
        case Success(c):
            conf = c

        case Failure(e):
            tmux_print(f"failed to load config: {e}")
            return 1

    # Update the cache if it doesn't exist or --update-cache is passed
    not_exist = not os.path.exists(conf["macros_cache_py"])
    if args.update_cache or not_exist:
        parse_macros_yml_and_generate_cache(conf) # TODO: look at and refactor this function
        if not_exist:
            tmux_print("⚠️ Cache not found. Regenerating...")
        else:
            # Since --update-cache was passed, this is where we stop
            return 0

    macros_dict: dict[str, Any]
    match load_cache(conf["macros_cache_py"]):
        case Some(spec):
            macros_dict = spec

        case Nothing:  # pyright: ignore[reportUnusedVariable]  # noqa: F811, F841
            tmux_print("Error: Unable load macro cache")
            return 1

    if args.macro:
        run_macro(macros_dict, args.macro)
    else:
        tmux_print("Error: No macro name provided.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

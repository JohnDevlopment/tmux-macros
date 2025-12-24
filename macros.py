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

from utils import load_conf, parse_macros_yml_and_generate_cache, tmux_print


def get_active_pane():
    return (
        subprocess.check_output(["tmux", "display-message", "-p", "#{pane_id}"])
        .decode("utf-8")
        .strip()
    )


def send_command_to_pane(pane_id, command):
    subprocess.run(["tmux", "send-keys", "-t", pane_id, command])


def run_macro(macros_dict, macro_name):
    # tmux_print(f"Running macro: {macro_name}")
    active_pane = get_active_pane()
    if macro_name not in macros_dict:
        tmux_print(f"Macro '{macro_name}' not found.")
        return

    for c in macros_dict[macro_name]["commands"]:
        if c["type"] == "text" or c["type"] == "keypress":
            send_command_to_pane(active_pane, c["value"])
        elif c["type"] == "sleep":
            sleep(0.001 * int(c["value"]))


def load_cache(location: str) -> Maybe[dict[str, Any]]:
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("macros_cache", location)
    if spec is None:
        return Nothing

    macros_cache = module_from_spec(spec)

    loader = spec.loader
    if loader is None:
        return Nothing

    loader.exec_module(macros_cache)
    macros_dict = macros_cache.MACROS

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

    if args.update_cache:
        parse_macros_yml_and_generate_cache(conf)
        return 1

    if not os.path.exists(conf["macros_cache_py"]):
        tmux_print("⚠️ Cache not found. Regenerating...")
        parse_macros_yml_and_generate_cache(conf)

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

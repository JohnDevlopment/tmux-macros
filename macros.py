#!/usr/bin/env -S python3 -O
"""
tmux-macros: A tool to run macros in tmux using Python scripts.
This script allows you to run predefined macros in tmux panes.
It reads macros from a YAML file, generates a cache, and allows execution of macros via command line arguments.
"""

import argparse
import os
import subprocess
from time import sleep

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("macro", nargs="?", help="Macro to execute")
    parser.add_argument(
        "--update-cache",
        action="store_true",
        help="Regenerate macros_cache.py and .tmux.macros.conf",
    )
    args = parser.parse_args()

    conf = load_conf()

    if args.update_cache:
        parse_macros_yml_and_generate_cache(conf)
        return

    if not os.path.exists(conf["macros_cache_py"]):
        tmux_print("⚠️ Cache not found. Regenerating...")
        parse_macros_yml_and_generate_cache(conf)

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("macros_cache", conf["macros_cache_py"])
    macros_cache = module_from_spec(spec)
    spec.loader.exec_module(macros_cache)
    macros_dict = macros_cache.MACROS

    if args.macro:
        run_macro(macros_dict, args.macro)
    else:
        tmux_print("No macro name provided.")


if __name__ == "__main__":
    main()

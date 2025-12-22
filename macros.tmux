#!/usr/bin/env bash
#======================================================
#   Author: Ankit Mishra
#    Email: ankvats21@gmail.com
#  Created: 2025-07-25
#======================================================

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TMUX_CONF="$HOME/.config/tmux/tmux.conf"

# Add sourcing line to $TMUX_CONF only if not already present
MACROS_CONF_LINE="source-file \"$CURRENT_DIR/.tmux.macros.conf\""
if ! grep -Fq "$MACROS_CONF_LINE" "$TMUX_CONF"; then
    echo "$MACROS_CONF_LINE" >> "$TMUX_CONF"
fi

# Regenerate macro cache if not exists
if [ ! -f "$CURRENT_DIR/macros_cache.py" ]; then
    python3 "$CURRENT_DIR/macros.py" --update-cache
fi

# Always regenerate (if updated macros.yml)
tmux run-shell "python3 $CURRENT_DIR/macros.py --update-cache"

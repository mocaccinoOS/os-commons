#!/bin/sh
if [ -n "${WAYLAND_DISPLAY}" ]; then
    exec sudo -E WAYLAND_DISPLAY="${WAYLAND_DISPLAY}" \
                XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR}" \
                QT_QPA_PLATFORM=wayland \
                "/usr/bin/calamares" "$@"
else
    exec sudo "/usr/bin/calamares" "$@"
fi
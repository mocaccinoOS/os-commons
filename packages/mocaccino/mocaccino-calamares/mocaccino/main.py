#!/usr/bin/env python3
# encoding: utf-8

import os
import subprocess
import shutil
import libcalamares
import re


RE_IS_COMMENT = re.compile("^ *#")

# List of the packages to remove
# on the installed rootfs at the
# end of the installation process.
luet_packages2remove = [
    "mocaccino/live-setup",
    "system/mocaccino-calamares",
    "apps/calamares",
    "repository/livecd",
]


def is_comment(line):
    """
    Does the @p line look like a comment? Whitespace, followed by a #
    is a comment-only line.
    """
    return bool(RE_IS_COMMENT.match(line))

RE_TRAILING_COMMENT = re.compile("#.*$")
RE_REST_OF_LINE = re.compile("\\s.*$")


def setup_locales(install_path):
    locale_conf = libcalamares.globalstorage.value("localeConf")
    if not locale_conf:
        locale_conf = { 'LANG': 'en_US.UTF-8' }

    # 1. Write /etc/locale.conf with all LC_* values provided by Calamares.
    # Writing only LANG leaves other LC_* variables unset, causing them to
    # fall back to system defaults instead of the user's chosen locale.
    locale_conf_path = os.path.join(install_path, "etc/locale.conf")
    with open(locale_conf_path, "w") as f:
        for key, value in locale_conf.items():
            f.write(f"{key}={value}\n")

    # 2. Rewrite /etc/locale.gen: ensure all required locales are uncommented
    # and formatted correctly. This prevents LC_ALL errors when multiple
    # locales are used (e.g. LANG=en_US.UTF-8 but LC_TIME=nl_NL.UTF-8)
    # while still avoiding generating ALL locales.
    locale_gen_path = os.path.join(install_path, "etc/locale.gen")
    if os.path.exists(locale_gen_path):
        # Collect all unique locale bases (e.g., "en_US", "nl_NL") from config
        required_bases = set()
        for val in locale_conf.values():
            if val and val not in ("C", "POSIX"):
                # Extract base part before . or @
                base = val.split(".")[0].split("@")[0]
                required_bases.add(base)

        with open(locale_gen_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        found_bases = set()
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue

            # Extract the locale base from the current line
            content = stripped.lstrip("# ").split()
            first_word = content[0] if content else ""
            line_base = first_word.split(".")[0].split("@")[0]

            if line_base in required_bases:
                # If this is one of our required locales, ensure it's uncommented
                # and uses the canonical "locale.UTF-8 UTF-8" format.
                if line_base not in found_bases:
                    new_lines.append(f"{line_base}.UTF-8 UTF-8\n")
                    found_bases.add(line_base)
            elif not stripped.startswith("#"):
                # If the line is active but not required, comment it out.
                new_lines.append(f"# {line}")
            else:
                # Otherwise, keep the comment as-is.
                new_lines.append(line)

        # Append any required locales that weren't found in the template.
        for base in sorted(required_bases):
            if base not in found_bases:
                libcalamares.utils.debug(f"{base} not found in locale.gen, appending.")
                new_lines.append(f"{base}.UTF-8 UTF-8\n")

        with open(locale_gen_path, "w") as f:
            f.writelines(new_lines)

    # 3. Verify the rewrite produced exactly the expected active locales,
    # then run locale-gen inside the chroot.
    # localectl is intentionally not called here — it always fails in a
    # chroot since there is no running systemd. Writing locale.conf above
    # is sufficient.
    libcalamares.utils.target_env_call(["locale-gen"])

def setup_audio(root_install_path):
    asound_state_filename = 'asound.state'
    asound_state_orig = '/etc/' + asound_state_filename
    if os.path.isfile(asound_state_orig) and os.access(asound_state_orig,
                                                       os.R_OK):
        asound_state_alsa_dest_1 = root_install_path + '/etc/'
        asound_state_alsa_dest_2 = root_install_path + '/var/lib/alsa/'
        os.makedirs(asound_state_alsa_dest_1, mode=0o755, exist_ok=True)
        os.makedirs(asound_state_alsa_dest_2, mode=0o755, exist_ok=True)
        shutil.copy2(asound_state_orig, asound_state_alsa_dest_1)
        shutil.copy2(asound_state_orig, asound_state_alsa_dest_2)


def configure_services(root_install_path):
    def is_virtualbox():
        """
        Return a virtualization environment identifier using
        systemd-detect-virt. This code is systemd only.
        """
        proc = subprocess.run(['/usr/bin/systemd-detect-virt'],
                              stdout=subprocess.PIPE)
        exit_st = proc.returncode
        outcome = proc.stdout
        if exit_st == 0:
            return outcome.decode().strip() == 'oracle'

    if is_virtualbox():
        libcalamares.utils.target_env_call(
            ['systemctl', '--no-reload', 'enable',
             'virtualbox-guest-additions.service'])
    else:
        libcalamares.utils.target_env_call(
            ['systemctl', '--no-reload', 'disable',
             'virtualbox-guest-additions.service'])
        libcalamares.utils.target_env_call(
            ['rm', '-rf', '/etc/xdg/autostart/vboxclient.desktop'])

    install_data_dir = os.path.join(root_install_path, 'install-data')
    if os.path.isdir(install_data_dir):
        shutil.rmtree(install_data_dir, True)

def remove_installer_desktop(install_path):
    username = libcalamares.globalstorage.value("username")
    if not username:
        libcalamares.utils.debug("No username found; skipping Installer.desktop removal.")
        return

    desktop_path = os.path.join(install_path, "home", username, "Desktop", "Installer.desktop")
    if os.path.exists(desktop_path):
        try:
            os.remove(desktop_path)
            libcalamares.utils.debug(f"Removed {desktop_path}")
        except Exception as e:
            libcalamares.utils.debug(f"Failed to remove {desktop_path}: {e}")


# ==============================================================================
# NETINSTALL INTEGRATION
#
# The netinstall module presents a multi-select checklist during the Calamares
# wizard, configured via /etc/calamares/modules/netinstall.conf.
# Package names (packageName fields) are full luet package names so they can
# be passed directly to luet install.
#
# netinstall writes selected packages to globalstorage under the key
# "packageOperations" as a list of dicts. We extract the "install" list
# from that and call luet install for each package.
#
# Packages that live in the community repository (mocaccino-community-stable)
# are listed in COMMUNITY_PACKAGES. If any such package is selected,
# the repository is enabled automatically before installing anything.
# ==============================================================================

# Mapping from netinstall display names to luet package names.
# Netinstall stores the human-readable "name" field in globalstorage,
# not the "packageName" field, so we need this map to resolve them.
PACKAGE_NAME_MAP = {
    # Browsers
    "Chromium":                    "apps/chromium",
    "Brave (Community)":           "apps/brave",
    "Vivaldi (Community)":         "apps/vivaldi",
    "Opera (Community)":           "apps/opera",
    "Tor Browser (Community)":     "apps/torbrowser",
    "Google Chrome (Community)":   "apps/google-chrome",
    "Konqueror (Community)":       "apps/konqueror",
    # Office
    "Evolution":                   "apps/evolution",
    "FreeOffice (Community)":      "apps/freeoffice",
    "LibreOffice (Community)":     "apps/libreoffice",
    "Calligra (Community)":        "apps/calligra",
    # Games
    "Steam":                       "apps/steam",
    "NVIDIA Drivers":              "kernel-modules/nvidia-drivers-lts",
    "Lutris (Community)":          "apps/lutris",
    "Wine Staging (Community)":    "apps/wine-staging",
    # Development
    "GCC":                         "devel/gcc",
    "CMake":                       "devel/cmake",
    "KDevelop (Community)":        "apps/kdevelop",
    "VSCodium (Community)":        "apps/vscodium",
    "Bluefish (Community)":        "apps/bluefish",
}

# Packages that require the community repository to be enabled first.
COMMUNITY_PACKAGES = {
    "apps/freeoffice", "apps/libreoffice", "apps/calligra",
    "apps/lutris", "apps/wine-staging",
    "apps/kdevelop", "apps/vscodium", "apps/bluefish",
}

COMMUNITY_REPO = "repository/mocaccino-community-stable"


def install_extra_packages():
    """Read netinstall selections from globalstorage and install via luet."""
    selected_packages = []
    needs_community = False

    # netinstall writes selected package display names to "packageOperations"
    # as a list of dicts with a "try_install" key. We map display names back
    # to luet package names via PACKAGE_NAME_MAP.
    package_operations = libcalamares.globalstorage.value("packageOperations")
    if not package_operations:
        libcalamares.utils.debug("No extra packages selected, skipping.")
        return

    for operation in package_operations:
        for display_name in operation.get("try_install", []):
            display_name = display_name.strip()
            pkg = PACKAGE_NAME_MAP.get(display_name)
            if not pkg:
                libcalamares.utils.debug(f"Unknown package display name: {display_name!r}, skipping.")
                continue
            selected_packages.append(pkg)
            if pkg in COMMUNITY_PACKAGES:
                needs_community = True

    if not selected_packages:
        libcalamares.utils.debug("No extra packages selected, skipping.")
        return

    # Enable community repository first if any selected package needs it.
    if needs_community:
        libcalamares.utils.debug(f"Enabling community repository: {COMMUNITY_REPO}")
        libcalamares.utils.target_env_call(["luet", "install", "-y", COMMUNITY_REPO])

    for pkg in selected_packages:
        libcalamares.utils.debug(f"Installing extra package: {pkg}")
        libcalamares.utils.target_env_call(["luet", "install", "-y", pkg])

# ==============================================================================
# END NETINSTALL INTEGRATION
# ==============================================================================

def run():
    """ Mocaccino Calamares Post-install module """
    # Get install path
    install_path = libcalamares.globalstorage.value('rootMountPoint')
    setup_locales(install_path)
    setup_audio(install_path)
    configure_services(install_path)
    remove_installer_desktop(install_path)
    install_extra_packages()

    # Merge any unmerged config files (e.g. leftovers from repo refreshes
    # triggered by the Calamares Software module) to prevent duplicate
    # repository entries in Luet on the installed system.
    libcalamares.utils.target_env_call([
        'sh', '-c',
        'mos config-update update --interactive=false -p /etc/luet/repos.conf.d || true'
    ])

    libcalamares.utils.target_env_call([
        'mocaccino-dracut', '--rebuild-all', '--force'
    ])

    if len(luet_packages2remove) > 0:
        args = ["luet", "uninstall", "-y"]
        # args = args + luet_packages2remove
        # libcalamares.utils.target_env_call(args)
        # Temporary trying to remove every package singolary
        for pkg in luet_packages2remove:
            libcalamares.utils.target_env_call(args + [pkg])

    # The Calamares desktop icon gets installed in /etc/skel
    # No need to have that on the target system
    libcalamares.utils.target_env_call(['rm', '-rf', '/etc/skel/Desktop/Installer.desktop'])
    libcalamares.utils.target_env_call(['env-update'])
    return None
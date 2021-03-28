#!/usr/bin/env python3
# encoding: utf-8

import os
import subprocess
import shutil
import libcalamares
import re


RE_IS_COMMENT = re.compile("^ *#")


def is_comment(line):
    """
    Does the @p line look like a comment? Whitespace, followed by a #
    is a comment-only line.
    """
    return bool(RE_IS_COMMENT.match(line))

RE_TRAILING_COMMENT = re.compile("#.*$")
RE_REST_OF_LINE = re.compile("\\s.*$")


def extract_locale(line):
    """
    Extracts a locale from the @p line, and returns a pair of
    (extracted-locale, uncommented line). The locale is the
    first word of the line after uncommenting (in the human-
    readable text explanation at the top of most /etc/locale.gen
    files, the locales may be bogus -- either "" or e.g. "Configuration")
    """
    # Remove leading spaces and comment signs
    line = RE_IS_COMMENT.sub("", line)
    uncommented = line.strip()
    fields = RE_TRAILING_COMMENT.sub("", uncommented).strip().split()
    if len(fields) != 2:
        # Not exactly two fields, can't be a proper locale line
        return "", uncommented
    else:
        # Drop all but first field
        locale = RE_REST_OF_LINE.sub("", uncommented)
        return locale, uncommented

def set_grub_background():
    libcalamares.utils.target_env_call(['mkdir', '-p', '/boot/grub/'])
    libcalamares.utils.target_env_call(
        ['cp', '-f', '/usr/share/grub/default-splash.png',
         '/boot/grub/default-splash.png'])


def setup_locales(install_path):
    locale_conf = libcalamares.globalstorage.value("localeConf")

    if not locale_conf:
        locale_conf = {
            'LANG': 'en_US.utf-8',
            'LC_NUMERIC': 'en_US.utf-8',
            'LC_TIME': 'en_US.utf-8',
            'LC_MONETARY': 'en_US.utf-8',
            'LC_PAPER': 'en_US.utf-8',
            'LC_NAME': 'en_US.utf-8',
            'LC_ADDRESS': 'en_US.utf-8',
            'LC_TELEPHONE': 'en_US.utf-8',
            'LC_MEASUREMENT': 'en_US.utf-8',
            'LC_IDENTIFICATION': 'en_US.utf-8'
        }

    target_locale_gen = "{!s}/etc/locale.gen".format(install_path)
    target_locale_gen_bak = target_locale_gen + ".bak"
    target_etc_default_path = "{!s}/etc/env.d/02locale".format(install_path)

    # restore backup if available
    if os.path.exists(target_locale_gen_bak):
        shutil.copy2(target_locale_gen_bak, target_locale_gen)
        libcalamares.utils.debug(
                "Restored backup {!s} -> {!s}"
                .format(target_locale_gen_bak, target_locale_gen))

    libcalamares.utils.target_env_call(['locale-gen', '-A'])
    libcalamares.utils.target_env_call([
        'localect', 'set-locale', locale_conf['LANG']
    ])

    # write /etc/default/locale if /etc/default exists and is a dir
    if os.path.isdir(target_etc_default_path):
        with open(os.path.join(target_etc_default_path, "locale"), "w") as edl:
            for k, v in locale_conf.items():
                edl.write("{!s}={!s}\n".format(k, v))
        libcalamares.utils.debug('{!s} done'.format(target_etc_default_path))


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


def run():
    """ Mocaccino Calamares Post-install module """
    libcalamares.utils.target_env_call([
        'mocaccino-dracut', '--rebuild-all', '--force'
    ])
    # Get install path
    install_path = libcalamares.globalstorage.value('rootMountPoint')
    set_grub_background()
    setup_locales(install_path)
    setup_audio(install_path)
    configure_services(install_path)
    # Temporary workaround until we fix this in luet
    libcalamares.utils.target_env_call([
        'chown', '-R', 'gdm:gdm', '/var/lib/gdm/'
    ])
    libcalamares.utils.target_env_call(['env-update'])

    return None

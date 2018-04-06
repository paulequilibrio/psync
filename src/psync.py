# Psync - a naive tool for syncing partitions using rsync
# Copyright (C) 2018  Paulo Alexandre Aquino da Costa
# < contact at pauloalexandre dot com >
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""psync - A naive tool for syncing partitions using rsync

Usage:
  psync [<sections>...] [--verbose | --quiet] [options]
  psync (-h | --help)
  psync --version

Options:
  --version           Show version.
  -h --help           Show this screen.
  -v --verbose        Show more info.
  -q --quiet          Show no info.
  -d --dry            Run psync without doing anything. Just testing.
  -r --reverse        Run rsync from target to source.
  -c --config <file>  Load custom config [default: ~/.config/psync/config.yaml]

"""

import os
import sys
from datetime import datetime
from docopt import docopt

from src import helpers
from src import bash
sys.tracebacklimit = 0

version = "v0.1.0"
info = """Psync {0} - A naive tool for syncing partitions using rsync
Copyright (C) 2018 Paulo Alexandre Aquino da Costa""".format(version)

arguments = docopt(__doc__, version=info)

dry = arguments['--dry']
quiet = arguments['--quiet']
verbose = arguments['--verbose']
reverse = arguments['--reverse']

info = helpers.log('INFO', quiet)
warning = helpers.log('WARNING', quiet)
error = helpers.log('ERROR', quiet)

if not os.geteuid() == 0:
    sys.exit("\nYou need root (sudo) permission to run this\n")

config_path = helpers.resolve_path(arguments['--config'])
config = helpers.load_config(config_path)

actual_hostname = bash.get_hostname()

info("psync", version, "started on host '" + actual_hostname + "'\n")
info("using config file '" + os.path.abspath(config_path) + "'")


def main():
    time = {'total': {}}
    time['total']['start'] = datetime.now()

    config_sections = list(dict.fromkeys(config))
    argument_sections = list(dict.fromkeys(arguments['<sections>']))

    [sections, no] = helpers.check_sections(config_sections, argument_sections)

    info('sections in config file:', str(config_sections))

    if argument_sections:
        info('sections from command line:', str(argument_sections))

    if no:
        warning('ignored sections (not in config file):', str(no))

    info('the following sections will be synced:', str(sections), "\n")

    skipped = []

    for name in sections:
        time[name] = {}
        time[name]['start'] = datetime.now()

        section = config[name]
        [source, target] = bash.handle_reverse(section, reverse)
        hosts = (source['hostname'], target['hostname'])

        start_message = '[ {0} ] '.format(name)
        info_section = helpers.log(name, quiet)

        if not source['hostname']:
            info_section('sync')
            partition_sync(info_section, section, source, target)
        elif source['hostname'] == actual_hostname:
            info_section("sync hosts '{0}' => '{1}'".format(*hosts))
            partition_sync(info_section, section, source, target)
        else:
            warning("Run on host '{0}' to sync '{0}' => '{1}'".format(*hosts))
            warning("section '{0}' skipped".format(name))
            skipped.append(name)

        time[name]['end'] = datetime.now()
        time[name]['duration'] = time[name]['end'] - time[name]['start']
        section_duration = helpers.time_format(time[name]['duration'])

        if name not in skipped:
            info_section('duration {}'.format(section_duration))

        print()

    time['total']['end'] = datetime.now()
    time['total']['duration'] = time['total']['end'] - time['total']['start']

    for name in time:
        if name != 'total':
            if name not in skipped:
                duration = helpers.time_format(time[name]['duration'])
                info('{0} duration {1}'.format(name, duration))
            else:
                info(name, 'skipped')

    total_duration = helpers.time_format(time['total']['duration'])
    info('total duration {}\n'.format(total_duration))

    info("psync {0} finished on host '{1}'".format(version, actual_hostname))


def partition_sync(info_section, section, source, target):
    info_section(helpers.get_infoline())
    info_section('FROM  ', helpers.get_infoline(source))
    info_section('  TO  ', helpers.get_infoline(target))

    mounts = (target['device'], target['mountpoint'])

    if verbose:
        info_section('mounting {0} on {1}'.format(*mounts))

    if not dry:
        bash.run(['mount', '-U', target['uuid'], target['mountpoint']])

    if 'touch' in section:
        for touch in section['touch']:
            path = os.path.join(target['mountpoint'], touch)
            if verbose:
                info_section('touch', path)
            if not dry:
                bash.run(['touch', path])

    if 'rsync_exclude' in section:
        exclude = ['--exclude={"'+'","'.join(section['rsync_exclude'])+'"}']
    else:
        exclude = ['']

    src_mnt = helpers.trailing_slash(source['mountpoint'])
    tar_mnt = helpers.trailing_slash(target['mountpoint'])
    replicas = [src_mnt, tar_mnt]

    options = section['rsync_options']
    if quiet:
        options.append('--quiet')

    rsync = ['rsync'] + options + exclude + replicas

    if verbose:
        info_section(' '.join(rsync))
    else:
        info_section('rsync from {0} to {1}'.format(*replicas))

    if not dry:
        bash.run(rsync)

    if verbose:
        info_section('unmounting {0} from {1}'.format(*mounts))

    if not dry:
        bash.run(['sync', '--file-system', target['mountpoint']])
        bash.run(['umount', target['mountpoint']])

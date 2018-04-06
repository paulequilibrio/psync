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

import os
import sys
import yaml
from datetime import datetime, timedelta


def time_format(delta=0):
    if isinstance(delta, timedelta):
        return (datetime.min + delta).time().strftime('%H:%M:%S')
    else:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log(name, quiet):
    def func(*args):
        if not quiet:
            print(time_format() + ' [ ' + name + ' ] ' + ' '.join(args))
        else:
            return None
    return func


def get_user():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    else:
        return os.environ['USER']


def resolve_path(path):
    if path == '~/.config/psync/config.yaml':
        path = os.path.join('/home', get_user(), '.config/psync/config.yaml')
    return path


def load_config(path):
    return yaml.safe_load(open(path))


def trailing_slash(path):
    return os.path.join(path, '')


def check_sections(config_sections, argument_sections):
    if not argument_sections:
        return [config_sections, []]
    else:
        yes = []
        no = []
        for section in argument_sections:
            if section in config_sections:
                yes.append(section)
            else:
                no.append(section)
        return [yes, no]


def get_infoline(replica=None):
    if not replica:
        titles = ('', 'UUID', 'DEVICE', 'LABEL', 'MOUNTED ON')
        return '{0:<7}{1:<39}{2:<12}{3:<19}{4}'.format(*titles)
    else:
        uuid = format(replica['uuid'], '<38')
        device = format(replica['device'], '<11')
        label = format(replica['label'], '<18')
        mountpoint = replica['mountpoint']
        return '{0} {1} {2} {3}'.format(uuid, device, label, mountpoint)

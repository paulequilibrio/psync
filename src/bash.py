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

import subprocess


def get_output(command_list):
    sub = subprocess.run(command_list, check=True, stdout=subprocess.PIPE)
    return sub.stdout.decode('utf-8').strip()


def run(command_list):
    return subprocess.run(command_list, check=True)


def get_hostname():
    return get_output(['cat', '/etc/hostname'])


def get_device_from_uuid(uuid):
    return get_output(['findfs', 'UUID=' + uuid])


def get_info_from_device(device, info):
    return get_output(['lsblk', '-no', info, device])


def time_format(delta=0):
    if isinstance(delta, timedelta):
        return (datetime.min + delta).time().strftime('%H:%M:%S')
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_section_info(section, replica):
    uuid = section[replica]['uuid']
    device = get_device_from_uuid(uuid)
    host = section['hostnames'][replica] if 'hostnames' in section else None
    return {
        'uuid': uuid,
        'device': device,
        'filesystem': get_info_from_device(device, 'FSTYPE'),
        'label': get_info_from_device(device, 'LABEL'),
        'hostname': host
    }


def handle_reverse(section, reverse):
    if not reverse:
        source = get_section_info(section, 'source')
        target = get_section_info(section, 'target')
    else:
        source = get_section_info(section, 'target')
        target = get_section_info(section, 'source')

    source['mountpoint'] = get_info_from_device(source['device'], 'MOUNTPOINT')
    target['mountpoint'] = section['mount_path']

    return [source, target]

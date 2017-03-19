#!/usr/bin/env python

#
#   Autor: Julian Meyer <jm@julianmeyer.de>
#
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import boto
import boto.ec2
import os
import argparse
import fnmatch
import ConfigParser


class ansi_color:
    reset = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    grey = '\033[1;30m'
    yellow = '\033[33m'


def get_name(i, color=True):
    if 'Name' in i.tags:
        n = i.tags['Name']
    else:
        n = '???'
    n = n.ljust(40)[:40]
    if color:
        if i.state == 'running':
            n = ansi_color.green + n + ansi_color.reset
        elif (i.state == 'pending') or (i.state == 'shutting-down') or (i.state == 'stopping'):
            n = ansi_color.yellow + n + ansi_color.reset
        elif i.state == 'terminated':
            n = ansi_color.grey + n + ansi_color.reset
        else:
            n = ansi_color.red + n + ansi_color.reset

    return n


def get_privat_dns(i):
    return i.private_dns_name.rjust(48)


def get_private_ip(i):
    return str(i.private_ip_address).ljust(15)


def get_pub_dns(i):
    return i.public_dns_name.rjust(48)


def get_pub_ip(i):
    return str(i.ip_address).ljust(15)


def get_inst_type(i):
    return i.instance_type.ljust(12)


def get_inst_id(i):
    return i.id.ljust(19)


def get_inst_placement(i):
    return i.placement.ljust(12)


def print_list_head(region,total,up,down,other):
    place = 'Region: ' + region
    stats = 'total: ' + str(total) + ' - up: ' + str(up) + ' - down: ' + str(down) + ' - other: ' + str(other)
    print('')
    print(spacing + place + stats.rjust(153-len(place)))

    # table head
    title = []
    dash = []
    if args.view == 'public':
        view = 'Public'
    else:
        view = 'Private'

    title.append("Name".ljust(40))
    dash.append('-'*40)
    title.append(' | ' + (view + ' IP').ljust(15))
    dash.append('-|-' + '-'*15)
    title.append(' | ' + 'Inst. ID'.ljust(19))
    dash.append('-|-' + '-'*19)
    title.append(' | ' + 'A.-Zone'.ljust(13))
    dash.append('-|-' + '-'*13)
    title.append(' | ' + 'Inst. Type'.ljust(12))
    dash.append('-|-' + '-'*12)
    title.append(' | ' + (view + ' DNS').ljust(48))
    dash.append('-|-' + '-'*48)
    print(spacing+''.join(dash))
    print(spacing+''.join(title))
    print(spacing+''.join(dash))


def print_prog_banner():
    print(spacing + '-'*153)
    print(spacing + 'ec2list'.center(153))
    print(spacing + '-'*153)

def set_tty_name(profile_name):
    str_profile_name = ' ('+profile_name+')' if profile_name and str(profile_name) != 'default' else ''
    print('\033]0;ec2list' + str_profile_name + '\007')

def print_instances(instances,region, i_count_total, i_count_up, i_count_down, i_count_other):
    instances.sort()

    if args.showhead:
        print_list_head(region, i_count_total, i_count_up, i_count_down, i_count_other)

    for inst in instances:
        name, name_color, private_ip, inst_id, inst_placement, inst_type, pri_dns, pub_ip, pub_dns = inst
        if args.view == 'public':
            line = spacing + ' | '.join((name_color, pub_ip, inst_id, inst_placement, inst_type, pub_dns))
        else:
            line = spacing + ' | '.join((name_color, private_ip, inst_id, inst_placement, inst_type, pri_dns))
        print(line)

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

def configLoad():

    # Default Values
    parser_defaults = { "aws_profile":"default",
                        "region": ['eu-central-1'],
                        "view":"private",
                        "showtotal": False,
                        "showhead": True,
                        "showbanner": True,
                        "clearscreen": False,
                        "ttyrename": False
    }

    # Get Config File
    configfile = False
    if os.path.isfile(os.path.expanduser('~/.ec2list')):
        configfile = '~/.ec2list'
    else:
        if os.path.isfile(os.path.expanduser('~/.aws/ec2list')):
            configfile = '~/.aws/ec2list'


    if configfile:
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.expanduser(configfile))
        if config.has_section('default'):
            parser_defaults.update(dict(config.items('default')))


    parser = argparse.ArgumentParser(description="Script for commandline worker, to list your ec2 instances. "
                                                 "Support's awscli/boto profiles and multiple aws regions.")

    parser.set_defaults(**parser_defaults)

    parser.add_argument("--region", dest = 'region', required=False, nargs='+',
                        help="AWS Region(s) you wish to look for instances. Specific the region(s) or 'all'")
    parser.add_argument("--profile", dest = 'aws_profile', required=False,
                        help="The profile config you want to use from awscli/boto")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--public', dest = 'view', action='store_const', const='public', help="show public ip/dns")
    group.add_argument('--private', dest = 'view', action='store_const', const='private', help="show private ip/dns")

    parser.add_argument("--total", dest = 'showtotal', required=False,
                        action='store_true', help="show total list, not per region")
    parser.add_argument("-nh", "--no-head", dest = 'showhead', required=False, action='store_false',
                        help="don't show table head")
    parser.add_argument("-nb", "--no-banner", dest = 'showbanner', required=False, action='store_false',
                        help="don't show programm")
    parser.add_argument("-cls", "--clear-screen", dest = 'clearscreen', required=False, action='store_true',
                        help="Clear screen before printing output")
    parser.add_argument("--ttyrename", dest = 'ttyrename', required=False, action='store_true',
                        help="set terminal name")


    # Profile Config
    config_profile_name = parser.parse_args().aws_profile
    if configfile and config_profile_name and config.has_section(config_profile_name):
        parser_defaults.update(dict(config.items(config_profile_name)))
        parser.set_defaults(**parser_defaults)

    final_config = parser.parse_args()

    # Convert ini file values to correct type
    final_config.showtotal = str2bool(final_config.showtotal)
    final_config.showhead = str2bool(final_config.showhead)
    final_config.showbanner = str2bool(final_config.showbanner)
    final_config.clearscreen = str2bool(final_config.clearscreen)
    final_config.view = 'public' if final_config.view.lower() == 'public' else 'private'
    if isinstance(final_config.region, str):
        final_config.region =  final_config.region.replace(" ", "").split(',')

    return final_config


def main():

    # Get Args
    global args
    args = configLoad()

    # All or specific regions?
    if len(args.region) == 1 and args.region[0] == "all":
        rr = boto.ec2.regions()
        rr.sort(key=lambda x: x.name)
    elif len(args.region) == 1 and (("*" in str(args.region)) or ("?" in str(args.region))):
        rr = []
        for x in boto.ec2.regions():
            if fnmatch.fnmatch(str(getattr(x,'name')), str(args.region)[2:-2]):
                rr.append(x)
        rr.sort(key=lambda x: x.name)
    else:
        rr = [boto.ec2.get_region(x) for x in args.region]

    # layout screen
    global spacing
    if args.showhead:
        spacing = ' '
    else:
        spacing = ''

    if args.clearscreen :
        os.system('cls' if os.name == 'nt' else 'clear')

    if args.ttyrename:
        set_tty_name(args.aws_profile)

    if args.showbanner:
        print_prog_banner()

    # get instances and list it
    region_nr = 0
    for reg in rr:
        conn = reg.connect(profile_name=args.aws_profile)
        reservations = conn.get_all_instances()

        if (region_nr == 0 and args.showtotal is True) or args.showtotal is False:
            a_instances = []
            i_count_total = 0
            i_count_up = 0
            i_count_down = 0
            i_count_other = 0
        region_nr += 1

        for r in reservations:
            for i in r.instances:
                a_instances.append((get_name(i,False), get_name(i,True), get_private_ip(i), get_inst_id(i),
                                    get_inst_placement(i), get_inst_type(i), get_privat_dns(i), get_pub_ip(i), get_pub_dns(i)))
                if i.state == 'running':
                    i_count_up += 1
                elif i.state == 'stopped':
                    i_count_down += 1
                else:
                    i_count_other += 1
                i_count_total += 1

        if args.showtotal is False:
            print_instances(a_instances, reg.name, i_count_total, i_count_up, i_count_down, i_count_other)

    if args.showtotal is True:
        if region_nr == 1:
            print_instances(a_instances, reg.name, i_count_total, i_count_up, i_count_down, i_count_other)
        else:
            print_instances(a_instances, 'multiple '+ str(region_nr), i_count_total, i_count_up, i_count_down, i_count_other)

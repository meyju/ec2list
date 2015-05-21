#!/usr/bin/python

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
    return i.id.ljust(10)


def get_inst_placement(i):
    return i.placement.ljust(12)


def print_list_head(region,total,up,down,other):
    place = 'Region: ' + region
    stats = 'total: ' + str(total) + ' - up: ' + str(up) + ' - down: ' + str(down) + ' - other: ' + str(other)
    # main head
    print(spacing + '='*len(place))
    print(spacing + place)
    print(spacing + '='*len(place) + stats.rjust(153-len(place)))

    # table head
    title = []
    dash = []
    if args.pub:
        view = 'Public'
    else:
        view = 'Private'

    title.append("Name".ljust(40))
    dash.append('-'*40)
    title.append(' | ' + (view + ' IP').ljust(15))
    dash.append('-|-' + '-'*15)
    title.append(' | ' + 'Inst. ID'.ljust(10))
    dash.append('-|-' + '-'*10)
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
    print(spacing + '########   ######    #######   ##        ####   ######   ########')
    print(spacing + '##        ##    ##  ##     ##  ##         ##   ##    ##     ##   ')
    print(spacing + '##        ##               ##  ##         ##   ##           ##   ')
    print(spacing + '######    ##         #######   ##         ##    ######      ##   ')
    print(spacing + '##        ##        ##         ##         ##         ##     ##   ')
    print(spacing + '##        ##    ##  ##         ##         ##   ##    ##     ##   ')
    print(spacing + '########   ######   #########  ########  ####   ######      ##   ')
    print(spacing)


def defineParser():
    parser = argparse.ArgumentParser(description="Script for commandline worker, to list your ec2 instances. "
                                                 "Support's awscli/boto profiles and multiple aws regions.")

    parser.add_argument("--region", dest = 'aws_region', required=False, nargs='+', default=['eu-central-1'],
                        help="AWS Region(s) you wish to look for instances. Specific the region(s) or 'all'")
    parser.add_argument("--profile", dest = 'aws_profile', required=False, default='default',
                        help="The profile config you want to use from awscli/boto")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--public', dest = 'pub', action='store_true', help="show public ip/dns")
    group.add_argument('--private', dest = 'priv', action='store_true', help="show private ip/dns (default)")

    parser.add_argument("-nh", "--no-head", dest = 'showhead', default=True, required=False,
                        action='store_false', help="don't show table head")
    parser.add_argument("-nb", "--no-banner", dest = 'showbanner', default=True, required=False,
                        action='store_false', help="don't show programm")
    parser.add_argument("-cls", "--clear-screen", dest = 'cls', required=False,
                        action='store_true', help="Clear screen before printing output")

    return parser


def main():

    # Get Args
    global args
    args = defineParser().parse_args()

    global spacing
    if args.showhead:
        spacing = ' '
    else:
        spacing = ''

    # All or specific regions?
    if len(args.aws_region) == 1 and args.aws_region[0] == "all":
        rr = boto.ec2.regions()
    else:
        rr = [boto.ec2.get_region(x) for x in args.aws_region]

    # Clear screen
    if args.cls:
        os.system('cls' if os.name == 'nt' else 'clear')

    if args.showbanner:
        print_prog_banner()

    for reg in rr:
        conn = reg.connect(profile_name=args.aws_profile)
        reservations = conn.get_all_instances()

        a_instances = []
        i_count_total = 0
        i_count_up = 0
        i_count_down = 0
        i_count_other = 0

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

        a_instances.sort()

        if args.showhead:
            print_list_head(reg.name, i_count_total, i_count_up, i_count_down, i_count_other)

        for inst in a_instances:
            name, name_color, private_ip, inst_id, inst_placement, inst_type, pri_dns, pub_ip, pub_dns = inst
            if args.pub:
                line = spacing + ' | '.join((name_color, pub_ip, inst_id, inst_placement, inst_type, pub_dns))
            else:
                line = spacing + ' | '.join((name_color, private_ip, inst_id, inst_placement, inst_type, pri_dns))
            print(line)

ec2list
=======
Script for commandline worker, to list your ec2 instances. Support's awscli/boto profiles and multiple aws regions.

![ec2list screenshot](_docs/img/ec2list.png?raw=true "ec2list screenshot")

# Requirements

- Python >= 2.6
- Boto >= 2.36.0


# Installation


Optionally create a virtual environment and activate it. Then just run
`pip install ec2list`.

For script usage, run:

    ec2list --help


# Examples

List instances from project1 profile

    ec2list --profile project1

List instances from the regions eu-central-1 and eu-west-1

    ec2list --region eu-central-1 eu-west-1

List instances in multiple regions via wildcard

    ec2list --region eu*


List instances from all regions

    ec2list --region all

List instances with minimal output

    ec2list --no-head --no-banner --clear-screen
    ec2list -nh -nb -cls
    
List all instances at once, not per region

    ec2list --region eu* --total


# Configuration

You need to have read access to Amazon EC2 api. Setup an appropriate IAM policy.

Setup your AWS Credentials:

_~/.aws/config_

    [default]
    region = eu-central-1
    [profile project1]
    region = eu-west-1

_~/.aws/credentials_

    [default]
    aws_access_key_id = <Your AWS Access Key ID>
    aws_secret_access_key = <Your AWS Secret Access Key>
    [project1]
    aws_access_key_id = <Your AWS Access Key ID>
    aws_secret_access_key = <Your AWS Secret Access Key>

For further information how to setup your credentials see the offical AWS Userguide:
[AWS Command Line Interface - Configuration](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-config-files)

## ec2list Configuration

You can also configure the behavior of ec2list. Write your configuration file either in `~/.ec2list` or `~/.aws/ec2list`. 

The configuration is processed and overwritten in this order: 

`coded default -> configfile 'default' section -> configfile 'profile' section -> commandline arguments`

Following Options can be writen in your config file:

* region <- specific the region or multiple to list your instances
* view <- 'public' or 'private' - which view do you want on the instances. 
* showtotal <- 'true' or 'false' - list all instances of multiple regions at once
* showhead <- 'true' or 'false' - show table head before listing your instances
* showbanner <- 'true' or 'false' - show program name before listing your instances
* clearscreen <- 'true' or 'false' - clear screen before listing your instances
* ttyrename <- 'true' or 'false' - rename your ssh session, useful if your are using multiple tabs

Here are some examples

    [default]
    ttyrename = true
    clearscreen = true
    view = private
    
    [project1]
    view = public
    region = eu-west-1, eu-central-1
    
    [project2]
    view = private
    region = eu-central-1
    
    [project3]
    view = private
    region = us-west-*
    showtotal = true
    
# Copyright

Copyright 2015 Julian Meyer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
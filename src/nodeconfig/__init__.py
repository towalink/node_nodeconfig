#!/usr/bin/env python3

"""nodeconfig.py: A command line tool for configuring and managing the services of a Towalink node."""

"""
Towalink
Copyright (C) 2020 Dirk Henrici

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

You can be released from the requirements of the license by purchasing
a commercial license.
"""

__author__ = "Dirk Henrici"
__license__ = "AGPL3" # + author has right to release in parallel under different licenses
__email__ = "towalink.nodeconfig@henrici.name"


import getopt
import logging
import os
import sys

from . import servicemanager


def usage():
    """Show information on command line arguments"""
    print('Usage: %s [-?|--help] [-l|--loglevel debug|info|error]' % sys.argv[0])
    print('Configures and manages the services of a Towalink node')
    print()
    print('  -?, --help                        show program usage')
    print('  -l, --loglevel debug|info|error   set the level of debug information')
    print('                                    default: info')
    print()
    print('Examples: %s --loglevel debug' % sys.argv[0])
    print()

def show_usage_and_exit():
    """Show information on command line arguments and exit with error"""
    print()
    usage()
    sys.exit(2)

def parseopts():
    """Check and parse the command line arguments"""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'l:?', ['help', 'loglevel='])
    except getopt.GetoptError as ex:
        # print help information and exit:
        print(ex)  # will print something like "option -a not recognized"
        show_usage_and_exit()
    loglevel = logging.INFO
    for o, a in opts:
        if o in ('-?', '--help'):
            show_usage_and_exit()
        elif o in ('-l', '--loglevel'):
            a = a.lower()
            if a == 'debug':
              loglevel = logging.DEBUG
            elif a == 'info':
              loglevel = logging.INFO
            elif a == 'error':
              loglevel = logging.ERROR
            else:
                print('invalid loglevel')
                show_usage_and_exit()
        elif o in ('-c', '--check'):
            check = True
        else:
            assert False, 'unhandled option'
    if len(args) > 0:
        print('no arguments expected')
        show_usage_and_exit()
    return loglevel

def get_active_confdir():
    """Gets the path of the currently active configuration directory"""
    confdir = '/etc/towalink/configs'
    if not os.path.isdir(confdir):
        print(f'Configuration directory [{confdir}] not found')
        show_usage_and_exit()
    filename = os.path.join(confdir, 'active')
    if not os.path.islink(filename):
        print(f'Link [{filename}] for referencing active configuration not found')
        show_usage_and_exit()
    confdir = filename
    if not os.path.isdir(confdir):
        print(f'Active configuration directory [{confdir}] not found')
        show_usage_and_exit()
    return confdir

def main():
    """Main function"""
    loglevel = parseopts()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s: %(message)s', level=loglevel)  # use %(name)s instead of %(module) to include hierarchy information, see https://docs.python.org/2/library/logging.html
    logger = logging.getLogger(__name__);
    confdir = get_active_confdir()
    logger.debug(f'Checking for config updates in [{confdir}]')    
    sm = servicemanager.ServiceManager(confdir)
    sm.update_all()
    logger.debug('Done')


if __name__ == "__main__":
    main()

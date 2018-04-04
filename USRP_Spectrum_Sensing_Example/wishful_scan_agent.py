#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
agent.py: remote WiSHFUL agent.

Usage:
   agent.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./agent -v --config ./agent_config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import logging
import signal
import yaml
import sys, os
import wishful_agent

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"

log = logging.getLogger('wishful_agent.main')
agent = wishful_agent.Agent()

def main(args):
    log.debug(args)

    config_file_path = args['--config']

    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    agent.load_config(config)
    agent.run()


if __name__ == "__main__":
    try:
        from docopt import docopt
    except:
        print("""
        Please install docopt using:
            pip install docopt==0.6.1
        For more refer to:
        https://github.com/docopt/docopt
        """)
        raise

    args = docopt(__doc__, version=__version__)

    log_level = logging.INFO  # default
    if args['--verbose']:
        log_level = logging.DEBUG
    elif args['--quiet']:
        log_level = logging.ERROR

    logfile = None
    if args['--logfile']:
        logfile = args['--logfile']

    logging.basicConfig(filename=logfile, level=log_level,
        format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

    try:
        main(args)
    except KeyboardInterrupt:
        log.debug("Agent exits")
    finally:
        log.debug("Exit")
        agent.stop()

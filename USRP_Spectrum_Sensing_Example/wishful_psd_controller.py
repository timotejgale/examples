#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_controller.py: Global WiSHFUL controller illustrating
the use of generators.

Usage:
   global_controller.py [options] [-q | -v]

Options:
   --logfile name      Name of the logfile
   --config configFile Config file path

Example:
   ./global_controller -v --config ./config.yaml

Other options:
   -h, --help          show this help message and exit
   -q, --quiet         print less text
   -v, --verbose       print more text
   --version           show version and exit
"""

import sys
import datetime
import logging
import wishful_controller
import gevent
import yaml
import random
import time
from scapy.all import *
import numpy as np
import wishful_upis as upis
from wishful_framework import TimeEvent, PktEvent, MovAvgFilter, PeakDetector, Match, Action, Permanance, PktMatch, FieldSelector

__version__ = "0.0.1"

log = logging.getLogger('wishful_controller.main')
controller = wishful_controller.Controller()
nodes = []

@controller.new_node_callback()
def new_node(node):
    nodes.append(node)
    print("New node appeared:")
    print(node)


@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node);
    print("NodeExit : NodeName : {} Reason : {}".format(node.name, reason))


@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    print("DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(group, node.name, cmd, data))


def main(args):
    log.debug(args)

    config_file_path = args['--config']
    config = None
    with open(config_file_path, 'r') as f:
        config = yaml.load(f)

    controller.load_config(config)
    controller.start()

    # wait for at least one node
    while len(nodes) < 1:
        gevent.sleep(1)

    # control loop
    loop_cnt = 0
    update_ival = 5
    iface = 'eno2'
    gain = "30"
    spb = "4194304"
    fftsize = "1024"
    numofchannel = "13"
    firstchannel = "2412000000"
    channelwidth = "20000000"
    channeloffset = "5000000"
    bps = "4"
    freqbegin = "2410000000"
    mode = "2"
    scand_running = False
    out_file = "/users/timotejg/psd_measurements_%s.csv" % datetime.now().isoformat()

    while True:
        while len(nodes) < 1:
            gevent.sleep(1)

        print("Connected nodes", [str(node.name) for node in nodes])
        loop_cnt += 1

        if nodes:

            print("Controller loop: %d." % loop_cnt)

            # start scanner daemon
            if not scand_running:
                print("Starting scanner daemon with params:")
                print("iface=%s, gain=%s, spb=%s, fftsize=%s, numofchannel=%s,\
                        firstchannel=%s, channelwidth=%s, channeloffset=%s, bps=%s,\
                        freqbegin=%s, mode=%s." % (iface, gain, spb, fftsize, numofchannel,\
                                                    firstchannel, channelwidth, channeloffset, bps, freqbegin, mode))
                controller.node(nodes[0]).radio.iface(iface).scand_start(iface=iface, gain=gain, spb=spb, fftsize=fftsize,\
                                                                          numofchannel=numofchannel, firstchannel=firstchannel,\
                                                                          channelwidth=channelwidth, channeloffset=channeloffset,\
                                                                          bps=bps, freqbegin=freqbegin, mode=mode)

                scand_running = True

            psd_pkts = controller.node(nodes[0]).radio.iface(iface).scand_read()

            if psd_pkts.any():
                print("Received PSD pkts of size:")
                shape = psd_pkts.shape
                print(shape)

		# print to file
                with open(out_file, 'a+') as out_f:
                    np.savetxt(out_f, psd_pkts, delimiter=",", fmt="%d")

            else:
                print("Received no PSD pkts.")

            gevent.sleep(update_ival)


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
        log.debug("Controller exits")
    finally:
        log.debug("Exit")
        controller.stop()

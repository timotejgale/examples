#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wishful IEEE 802.11 example consisting of two APs and two mobile STAs. Each AP is controlled by an
Wishful agent. Moreover, a global controller which is running on AP1 is controlling the two APs through
their agents.
"""

from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

from wishful_mininet import WishfulNode, WishfulAgent, WishfulController
import time

__author__ = "Piotr Gawlowicz, Anatolij Zubow"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"

# enable mininet cli
MN_CLI = False
# enable GUI
GUI = False
# enable mobility
MOBILITY = True

'''
Simple topology with two APs and two mobile STAs.

sudo python ./mn_script.py
'''
def topology():

    "Create a network."
    net = Mininet( controller=Controller, link=TCLink, switch=OVSKernelSwitch )

    print("*** Creating nodes")
    sta1 = net.addStation( 'sta1', mac='00:00:00:00:00:02', ip='10.0.0.2/8' )
    sta2 = net.addStation( 'sta2', mac='00:00:00:00:00:03', ip='10.0.0.3/8' )
    ap1 = net.addBaseStation( 'ap1', ssid= 'new-ssid1', mode= 'g', channel= '1', position='15,50,0' )
    ap2 = net.addBaseStation( 'ap2', ssid= 'new-ssid2', mode= 'g', channel= '6', position='25,30,0' )
    c1 = net.addController( 'c1', controller=Controller )

    print("*** Creating links")
    net.addLink(ap1, ap2)
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)

    print("*** Starting network")
    net.build()
    c1.start()
    ap1.start( [c1] )
    ap2.start( [c1] )

    "Configure IP addresses on APs for binding Wishful agent"
    ap1.cmd('ifconfig ap1-eth1 20.0.0.2/8')
    ap2.cmd('ifconfig ap2-eth1 20.0.0.3/8')

    print("*** Starting Wishful framework")
    folder = './'

    print("*** ... agents ...")
    agent1 = WishfulAgent(ap1, folder + 'agent', folder + 'agent1_cfg.yaml')
    agent2 = WishfulAgent(ap2, folder + 'agent', folder + 'agent2_cfg.yaml')
    agent1.start()
    agent2.start()

    print("*** ... controller ...")
    wf_ctrl = WishfulController(ap1, folder + 'global_controller', folder + 'controller_cfg.yaml')
    wf_ctrl.start()

    print("*** Starting network")

    """uncomment to plot graph"""
    if GUI:
        net.plotGraph(max_x=100, max_y=100)

    if MOBILITY:
        net.startMobility(startTime=0)
        net.mobility('sta1', 'start', time=0, position='10,45,0')
        net.mobility('sta1', 'stop', time=60, position='50,20,0')
        net.mobility('sta2', 'start', time=0, position='0,60,0')
        net.mobility('sta2', 'stop', time=60, position='30,10,0')
        net.stopMobility(stopTime=60)

    print("*** Starting network")

    print("*** wait for node discovery")
    time.sleep(3)

    print("*** perform ping")
    sta1.cmd('ping -c20 %s' % sta2.IP())

    print("*** Check that Wishful agents/controllers are still running ...")
    if not wf_ctrl.check_is_running() or not agent1.check_is_running() or not agent2.check_is_running():
        raise Exception("Error; wishful controller or agents not running; check logfiles ... ")
    else:
        print("*** Wishful agents/controllers: OK")

    if MN_CLI:
        print("*** Running CLI")
        CLI( net )

    # Show controller log file
    print('WiSHFUL agent #1 logfile content:')
    print(agent1.read_log_file())
    print('')

    print('WiSHFUL agent #2 logfile content:')
    print(agent2.read_log_file())
    print('')

    print('WiSHFUL controller logfile content:')
    print(wf_ctrl.read_log_file())
    print('')

    print("*** Stopping network")
    wf_ctrl.stop()    
    agent1.stop()
    agent2.stop()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()

#!/usr/bin/python

__author__ = "Pierluigi Gallo, Domenico Garlisi"
__copyright__ = "Copyright (c) 2016, CNIT"
__version__ = "0.1.0"
__email__ = "domenico.garlisi@cnit.it"

import sys
import subprocess
import time
import multiprocessing
from time import gmtime, strftime

from numpy import *
from datetime import datetime, date, timedelta

import matplotlib

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt, os, fnmatch
from matplotlib.backends.backend_pdf import PdfPages


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import json

"""
Starting from the stored experiment measurements this script creates 2 plots with protocol and throughput experiment
result.
"""
# loading data
with open('measure.json') as data_file:
	data = json.load(data_file)


#define data field
measurement_types=['TIME', 'BUSY_TIME', 'tx_activity', 'num_tx', 'num_tx_success']

# protocols_labels = ['', 'TDMA 0 (slot 0)', 'TDMA 1 (slot 1)', 'TDMA 2 (slot 2)', 'TDMA 3 (slot 3)', 'ALOHA p=0.9']
# protocols_tick = [0, 1, 2, 3, 4]

nodes = data.keys()

# order IP addresses of nodes and put read data in an array
# x = array(data.get(list(sort(data.keys()))[1]))
x = array(data.get('192.168.0.3'))

dim = x.shape
yaxis = [0] * dim[0]
my_dpi=100
width=1024
height=768


node_num = 0

nodes = data.keys()
#TODO: change the list, currently excludes 0.1 because this nodes does not provide measurements
# for node in list(sort(data.keys())):
# for node in nodes:
for node in list([u'192.168.0.3', u'192.168.0.5']):
	nodeIp=node
	node_num += 1
	x = array(data.get(nodeIp))
	#print("%s" % str(x))

	dim = x.shape
	xaxis = []

	if len(dim) > 2:
		number_type_measurements = dim[2]
	else:
		number_type_measurements = 1

	if number_type_measurements != len(measurement_types):
		print ('ERROR: %d measurements expected -  %d received' %(len(measurement_types), number_type_measurements))
		sys.exit('Mismatch in the number of measurements ')

	for meas_type_id in range(number_type_measurements):

		figure_id = 0
		fig = plt.figure(figure_id)
		fig.set_size_inches(width / my_dpi, height / my_dpi)

		#extract reference time information
		if measurement_types[meas_type_id] == "TIME" :
			min_time=np.min(x[:,0,meas_type_id])
			# print ("min_time %f" %(min_time))
			for ii in range(dim[0]):
				xaxis.append(x[ii][0][meas_type_id])
			# print ('xaxis = %s' %(str(xaxis)))

		#extract protocol information
		if measurement_types[meas_type_id] == "BUSY_TIME" :
			protocol_yaxis = []

			# cycle over nodes
			for ii in range(dim[0]):
				protocol_yaxis.append(x[ii][0][meas_type_id])

			protocol_yaxis_norm = [yvalue / 5000 for yvalue in protocol_yaxis]
			# remove the first 2 elements (which are not given by a difference but are absolute values)
			protocol_yaxis_norm[0:2] = [0] * 2
			print ('busy time = %s' % (str(protocol_yaxis_norm)))

			ax = fig.add_subplot(221)
			#nodeIp_label=nodeIp.replace("192.168.3.","sta")
			nodeIp_label = 'sta' + str(node_num)

			slot_time = 5
			ax.plot((xaxis-min_time), protocol_yaxis_norm, '-', label=nodeIp_label, linewidth=2.0);

			ax.grid(True)
			#ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))])
			#ax.set_ylim([-0.5, 5])

			ax.set_ylabel('Busy time / Total time');
			ax.set_xlabel('time [s]')
			ax.set_ylim([0,1])
			#ax.yticks(protocols_tick, protocols_labels)
			#locs, labels = ax.yticks()
			#ax.set_yticklabels(protocols_labels)

			# plt.tight_layout()
			legend = ax.legend(loc='lower center', ncol=3, fancybox=True, shadow=True)
			#legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

		if measurement_types[meas_type_id] == "tx_activity":
			protocol_yaxis = []

			# cycle over nodes
			for ii in range(dim[0]):
				protocol_yaxis.append(x[ii][0][meas_type_id])

			protocol_yaxis_norm = [yvalue/5000 for yvalue in protocol_yaxis]
			# remove the first 2 elements (which are not given by a difference but are absolute values)
			protocol_yaxis_norm[0:2] = [0] * 2
			print ('tx activity = %s' % (str(protocol_yaxis_norm)))

			# figure_id = 0
			# fig = plt.figure(figure_id)
			ax = fig.add_subplot(223)
			# nodeIp_label=nodeIp.replace("192.168.3.","sta")
			nodeIp_label = 'sta' + str(node_num)

			slot_time = 5
			time_values = (xaxis - min_time)

			ax.plot(time_values, protocol_yaxis_norm, '-', label=nodeIp_label, linewidth=2.0);

			ax.grid(True)
			# ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))])
			# ax.set_ylim([-0.5, 5])

			ax.set_ylabel('tx time / total time');
			ax.set_xlabel('time [s]')
			ax.set_ylim([0, 1])
			# ax.yticks(protocols_tick, protocols_labels)
			# locs, labels = ax.yticks()
			# ax.set_yticklabels(protocols_labels)

			# fig.set_size_inches(width / my_dpi, height / my_dpi)
			# plt.tight_layout()
			legend = ax.legend(loc='lower center', ncol=3, fancybox=True, shadow=True)
			# legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

		if measurement_types[meas_type_id] == "num_tx":

			protocol_yaxis = []

			# cycle over nodes
			for ii in range(dim[0]):
				protocol_yaxis.append(x[ii][0][meas_type_id])

			protocol_yaxis_norm = [yvalue/5 for yvalue in protocol_yaxis]
			# remove the first 2 elements (which are not given by a difference but are absolute values)
			protocol_yaxis_norm[0:2] = [0] * 2
			print ('num of tx = %s' % (str(protocol_yaxis_norm)))

			ax = fig.add_subplot(222)
			# nodeIp_label=nodeIp.replace("192.168.3.","sta")
			nodeIp_label = 'sta' + str(node_num)

			slot_time = 5
			time_values = (xaxis - min_time)
			ax.plot(time_values, protocol_yaxis_norm, '-', label=nodeIp_label, linewidth=2.0);
			ax.grid(True)
			# ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))])
			# ax.set_ylim([-0.5, 5])

			ax.set_ylabel('num of tx per second');
			ax.set_xlabel('time [s]')
			# ax.set_ylim([0, 1])
			# ax.yticks(protocols_tick, protocols_labels)
			# locs, labels = ax.yticks()
			# ax.set_yticklabels(protocols_labels)

			# fig.set_size_inches(width / my_dpi, height / my_dpi)
			# plt.tight_layout()
			legend = ax.legend(loc='lower center', ncol=3, fancybox=True, shadow=True)
			# legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)

		if measurement_types[meas_type_id] == "num_tx_success":
			protocol_yaxis = []

			# cycle over nodes
			for ii in range(dim[0]):
				protocol_yaxis.append(x[ii][0][meas_type_id])

			protocol_yaxis_norm = [yvalue / 5 for yvalue in protocol_yaxis]
			# remove the first 2 elements (which are not given by a difference but are absolute values)
			protocol_yaxis_norm[0:2] = [0] * 2
			print ('num_tx_success = %s' % (str(protocol_yaxis_norm)))

			ax = fig.add_subplot(224)
			# nodeIp_label=nodeIp.replace("192.168.3.","sta")
			nodeIp_label = 'sta' + str(node_num)

			slot_time = 5
			time_values = (xaxis - min_time)
			ax.plot(time_values, protocol_yaxis_norm, '-', label=nodeIp_label, linewidth=2.0);
			ax.grid(True)
			# ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))])
			# ax.set_ylim([-0.5, 5])

			ax.set_ylabel('successful tx per second');
			ax.set_xlabel('time [s]')
			# ax.set_ylim([0, 1])
			# ax.yticks(protocols_tick, protocols_labels)
			# locs, labels = ax.yticks()
			# ax.set_yticklabels(protocols_labels)

			# fig.set_size_inches(width / my_dpi, height / my_dpi)
			# plt.tight_layout()
			legend = ax.legend(loc='lower center', ncol=3, fancybox=True, shadow=True)
		# legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=5, fancybox=True, shadow=True)


#generate pdf plot
fig.set_size_inches(width/my_dpi,height/my_dpi)
plt.tight_layout()

#plt.show()
fig_filename="fig_%s.pdf" % 'interference-recognition'
fig.savefig(fig_filename, format='pdf')

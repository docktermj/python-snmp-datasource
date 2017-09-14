#!/usr/bin/python
# encoding: utf-8
'''
snmp_datasource -- A wrapper for `snmpget` that uses `stdin` for configuration.
'''

import fileinput
import logging
import subprocess
import sys
import time


__all__ = []
__version__ = 1.0
__date__ = '2017-09-14'
__updated__ = '2017-09-14'

# "snmpget" result array indicies.

SNMP_NAME = 0
SNMP_EQUALS = 1
SNMP_DATATYPE = 2
SNMP_VALUE = 3

# MIB names.

MIB_MY_SEPARATOR = "___"
MIB_MY = "my::"
MIB_MY_RATE = "my" + MIB_MY_SEPARATOR
MIB_MY_IP_ADDRESS = "my::ip-address"
MIB_MY_TIMESTAMP = "my::timestamp"

#  Define input and output  dictionaries

inputData = {}
inputMetaData = {}
inputRate = {}
snmpData = {}
outputData = {}


def process_line(line):
    ''' Process a line in the format: "MetricName = Datatype: value" '''

    splits = line.split()
    if splits[SNMP_NAME].startswith(MIB_MY):
        inputMetaData[splits[SNMP_NAME]] = splits
    elif splits[SNMP_NAME].startswith(MIB_MY_RATE):
        inputRate[splits[SNMP_NAME]] = splits
    else:
        inputData[splits[SNMP_NAME]] = splits


def read_stdin():
    ''' Read the configuration input from "stdin". '''

    for line in fileinput.input():
        process_line(line)
    if MIB_MY_TIMESTAMP not in inputMetaData:
        inputMetaData[MIB_MY_TIMESTAMP] = [MIB_MY_TIMESTAMP, '=', "Counter32", "0"]


def read_snmp():
    ''' Make call to snmpget to get current values. '''

    ip_address = inputMetaData[MIB_MY_IP_ADDRESS][SNMP_VALUE]
    args = ['snmpget', '-v', '1', '-c', 'public', ip_address] + inputData.keys()
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err != "":
        logging.error("ERROR: p.communicate() failed: " + err)
        return

    # Parse snmpget output stream into a dictionary of arrays.

    for line in out.splitlines():
        splits = line.split()
        snmpData[splits[SNMP_NAME]] = splits


def calculate_output_data():
    ''' Fill in the outputData dictionary. '''

    # Copy and update metadata.

    for key, value in inputMetaData.items():
        outputData[key] = value
    outputData[MIB_MY_TIMESTAMP] = [MIB_MY_TIMESTAMP, '=', "Counter32", time.time()]

    # Copy new SNMP data.

    for key, value in snmpData.items():
        outputData[key] = value

    # Calculate any "per second" data.

    deltaTime = outputData[MIB_MY_TIMESTAMP][SNMP_VALUE] - float(inputMetaData[MIB_MY_TIMESTAMP][SNMP_VALUE])
    for key, value in inputRate.items():
        parsedKey = key.split(MIB_MY_SEPARATOR)
        originalKey = parsedKey[1]
        deltaValue = int(snmpData[originalKey][SNMP_VALUE]) - int(inputData[originalKey][SNMP_VALUE])
        outputData[key] = value  # Copy entire original array.
        outputData[key][SNMP_VALUE] = deltaValue / deltaTime  # Update only the value.


def write_output():
    ''' Write output in MIB key sorted order. '''

    sortedKeys = sorted(outputData.keys())
    for key in sortedKeys:
        print("{} {} {} {}".format(*outputData[key]))


def main(argv=None):
    pass


# Main

if __name__ == "__main__":
    read_stdin()
    read_snmp()
    calculate_output_data()
    write_output()
    sys.exit(main())
WiSHFUL Spectral Scan USRP Example
============================

This is an example of a spectrum sensing experiment using USRP and *wishful_module_spectral_scan_usrp*.

## Usage

**Run example controller (run with -v for debugging)**
./wishful_simple_controller --config ./controller_config.yaml 

**Run example agent (run with -v for debugging)**
./wishful_simple_agent --config ./agent_config.yaml

## Notes

Please note that before running the example the *module_spectral_scan_usrp* must be installed and the following UPIs must be defined: radio.scand_start, radio.scand_stop, radio.scand_reconf, radio.scand_read.
Also set the IP on server interfaces that are connected to USRPs. IP address on server interfaces that are connected to USRPs must also be set.

This example is based on example *spectrum_sensing*.

## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
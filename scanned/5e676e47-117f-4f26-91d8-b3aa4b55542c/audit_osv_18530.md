# [M] CVE-2020-28349

## Summary
Severity: Medium
Advisory: CVE-2020-28349
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-09
Source: https://osv.dev/vulnerability/CVE-2020-28349
Type: osv

## Details
An inaccurate frame deduplication process in ChirpStack Network Server 3.9.0 allows a malicious gateway to perform uplink Denial of Service via malformed frequency attributes in CollectAndCallOnceCollect in internal/uplink/collect.go. NOTE: the vendor's position is that there are no "guarantees that allowing untrusted LoRa gateways to the network should still result in a secure network.

## References
- https://github.com/brocaar/chirpstack-network-server/commit/874fc1a9b01045ebe8a340f0bb01ed19e8256e60
- https://github.com/brocaar/chirpstack-network-server/commit/f996bb0c6c85281b5658f59ff09db1b4a73db453
- https://www.cyberark.com/resources/threat-research-blog/lorawan-mqtt-what-to-know-when-securing-your-iot-network

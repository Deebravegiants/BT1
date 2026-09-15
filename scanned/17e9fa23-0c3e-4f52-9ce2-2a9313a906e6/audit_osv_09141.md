# [C] CVE-2016-8598

## Summary
Severity: Critical
Advisory: CVE-2016-8598
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-28
Source: https://osv.dev/vulnerability/CVE-2016-8598
Type: osv

## Details
Buffer overflow in the zmq interface in csp_if_zmqhub.c in the libcsp library v1.4 and earlier allows hostile computers connected via a zmq interface to execute arbitrary code via a long packet.

## References
- http://www.securityfocus.com/bid/94226
- https://github.com/GomSpace/libcsp/pull/80

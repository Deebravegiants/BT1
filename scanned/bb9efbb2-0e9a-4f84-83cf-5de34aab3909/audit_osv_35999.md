# [C] CVE-2026-18664

## Summary
Severity: Critical
Advisory: CVE-2026-18664
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-18664
Type: osv

## Details
When ranges are used for access control (i.e. of the form 1.2.3.4-1.2.3.25), because NSD wrongly compares the IP address with the range on little endian systems, IPs that were meant to be allowed may be denied, and, IPs that were meant to be denied access could be allowed. An IPv4 address is compared with IPv4 ranges as unsigned 32 bit numbers directly with the endianness of the host, but the values to compare are in network byte order (big-endian).  With IPv6 addresses the comparison is done in 4 times a unsigned 32 bit number comparison, again with the endianness of the host where all values are actually in network bye order.

## References
- https://www.nlnetlabs.nl/downloads/nsd/CVE-2026-18664.txt

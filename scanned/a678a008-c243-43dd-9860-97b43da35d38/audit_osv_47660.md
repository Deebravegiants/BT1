# [H] CVE-2016-9918

## Summary
Severity: High
Advisory: CVE-2016-9918
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-9918
Type: osv

## Details
In BlueZ 5.42, an out-of-bounds read was identified in "packet_hexdump" function in "monitor/packet.c" source file. This issue can be triggered by processing a corrupted dump file and will result in btmon crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00054.html
- http://www.securityfocus.com/bid/95013
- https://www.spinics.net/lists/linux-bluetooth/msg68898.html

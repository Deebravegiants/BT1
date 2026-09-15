# [H] CVE-2016-5350

## Summary
Severity: High
Advisory: CVE-2016-5350
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5350
Type: osv

## Details
epan/dissectors/packet-dcerpc-spoolss.c in the SPOOLS component in Wireshark 1.12.x before 1.12.12 and 2.x before 2.0.4 mishandles unexpected offsets, which allows remote attackers to cause a denial of service (infinite loop) via a crafted packet.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91140
- http://www.debian.org/security/2016/dsa-3615
- http://www.openwall.com/lists/oss-security/2016/06/09/3
- https://www.wireshark.org/security/wnpa-sec-2016-29.html
- https://github.com/wireshark/wireshark/commit/b4d16b4495b732888e12baf5b8a7e9bf2665e22b

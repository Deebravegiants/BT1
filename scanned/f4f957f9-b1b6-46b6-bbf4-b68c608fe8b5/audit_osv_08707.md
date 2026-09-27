# [M] CVE-2016-5359

## Summary
Severity: Medium
Advisory: CVE-2016-5359
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5359
Type: osv

## Details
epan/dissectors/packet-wbxml.c in the WBXML dissector in Wireshark 1.12.x before 1.12.12 mishandles offsets, which allows remote attackers to cause a denial of service (integer overflow and infinite loop) via a crafted packet.

## References
- http://www.securityfocus.com/bid/91140
- http://www.debian.org/security/2016/dsa-3615
- https://www.wireshark.org/security/wnpa-sec-2016-38.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12408
- https://github.com/wireshark/wireshark/commit/b8e0d416898bb975a02c1b55883342edc5b4c9c0
- http://www.openwall.com/lists/oss-security/2016/06/09/3

# [M] CVE-2016-5357

## Summary
Severity: Medium
Advisory: CVE-2016-5357
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5357
Type: osv

## Details
wiretap/netscreen.c in the NetScreen file parser in Wireshark 1.12.x before 1.12.12 and 2.x before 2.0.4 mishandles sscanf unsigned-integer processing, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/91140
- http://www.debian.org/security/2016/dsa-3615
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- https://www.wireshark.org/security/wnpa-sec-2016-36.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12396
- https://github.com/wireshark/wireshark/commit/11edc83b98a61e890d7bb01855389d40e984ea82
- https://github.com/wireshark/wireshark/commit/6a140eca7b78b230f1f90a739a32257476513c78
- http://www.openwall.com/lists/oss-security/2016/06/09/3

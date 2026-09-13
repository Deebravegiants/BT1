# [M] CVE-2016-5352

## Summary
Severity: Medium
Advisory: CVE-2016-5352
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5352
Type: osv

## Details
epan/crypt/airpdcap.c in the IEEE 802.11 dissector in Wireshark 2.x before 2.0.4 mishandles certain length values, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91140
- https://www.wireshark.org/security/wnpa-sec-2016-31.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12175
- https://github.com/wireshark/wireshark/commit/b6d838eebf4456192360654092e5587c5207f185
- http://www.openwall.com/lists/oss-security/2016/06/09/3

# [H] CVE-2017-15191

## Summary
Severity: High
Advisory: CVE-2017-15191
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15191
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.1, 2.2.0 to 2.2.9, and 2.0.0 to 2.0.15, the DMP dissector could crash. This was addressed in epan/dissectors/packet-dmp.c by validating a string length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=8dbb21dfde14221dab09b6b9c7719b9067c1f06e
- http://www.securityfocus.com/bid/101227
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-44.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14068
- https://code.wireshark.org/review/23591

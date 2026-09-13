# [M] CVE-2018-19625

## Summary
Severity: Medium
Advisory: CVE-2018-19625
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19625
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.4 and 2.4.0 to 2.4.10, the dissection engine could crash. This was addressed in epan/tvbuff_composite.c by preventing a heap-based buffer over-read.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=dc4d209f39132a4ae05675a11609176ae9705cfc
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/106051
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-51.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14466

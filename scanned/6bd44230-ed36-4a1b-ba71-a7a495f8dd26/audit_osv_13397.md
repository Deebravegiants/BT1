# [M] CVE-2018-19626

## Summary
Severity: Medium
Advisory: CVE-2018-19626
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19626
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.4 and 2.4.0 to 2.4.10, the DCOM dissector could crash. This was addressed in epan/dissectors/packet-dcom.c by adding '\0' termination.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=c5a65115ebab55cfd5ce0a855c2256e01cab6449
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/106051
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-52.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15130

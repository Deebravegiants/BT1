# [H] CVE-2018-19628

## Summary
Severity: High
Advisory: CVE-2018-19628
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19628
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.4, the ZigBee ZCL dissector could crash. This was addressed in epan/dissectors/packet-zbee-zcl-lighting.c by preventing a divide-by-zero error.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=212b18825d9b668cda23d334c48867dfa66b2b36
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/106051
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-57.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15281

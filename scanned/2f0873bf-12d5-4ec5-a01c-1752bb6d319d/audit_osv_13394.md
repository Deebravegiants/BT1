# [H] CVE-2018-19623

## Summary
Severity: High
Advisory: CVE-2018-19623
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19623
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.4 and 2.4.0 to 2.4.10, the LBMPDM dissector could crash. In addition, a remote attacker could write arbitrary data to any memory locations before the packet-scoped memory. This was addressed in epan/dissectors/packet-lbmpdm.c by disallowing certain negative values.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=9c8645ec7b28e4d7193962ecd2a418613bf6a84f
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/106051
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-53.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15132

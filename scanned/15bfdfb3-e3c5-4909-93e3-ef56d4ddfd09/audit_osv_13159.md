# [H] CVE-2018-18227

## Summary
Severity: High
Advisory: CVE-2018-18227
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-12
Source: https://osv.dev/vulnerability/CVE-2018-18227
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.3 and 2.4.0 to 2.4.9, the MS-WSP protocol dissector could crash. This was addressed in epan/dissectors/packet-mswsp.c by properly handling NULL return values.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=d443be449a52f95df5754adc39e1f3472fec2f03
- https://www.oracle.com/security-alerts/cpuapr2020.html
- http://www.securityfocus.com/bid/105583
- http://www.securitytracker.com/id/1041909
- https://www.debian.org/security/2018/dsa-4359
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15119
- https://www.wireshark.org/security/wnpa-sec-2018-47.html

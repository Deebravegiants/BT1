# [H] CVE-2018-11354

## Summary
Severity: High
Advisory: CVE-2018-11354
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11354
Type: osv

## Details
In Wireshark 2.6.0, the IEEE 1905.1a dissector could crash. This was addressed in epan/dissectors/packet-ieee1905.c by making a certain correction to string handling.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=cb517a4a434387e74a2f75ebb106ee3c3893251c
- http://www.securityfocus.com/bid/104308
- http://www.securitytracker.com/id/1041036
- https://www.wireshark.org/security/wnpa-sec-2018-26.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14647

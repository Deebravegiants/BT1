# [H] CVE-2018-11362

## Summary
Severity: High
Advisory: CVE-2018-11362
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11362
Type: osv

## Details
In Wireshark 2.6.0, 2.4.0 to 2.4.6, and 2.2.0 to 2.2.14, the LDSS dissector could crash. This was addressed in epan/dissectors/packet-ldss.c by avoiding a buffer over-read upon encountering a missing '\0' character.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f177008b04a530640de835ca878892e58b826d58
- http://www.securityfocus.com/bid/104308
- http://www.securitytracker.com/id/1041036
- https://lists.debian.org/debian-lts-announce/2018/05/msg00019.html
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-25.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14615

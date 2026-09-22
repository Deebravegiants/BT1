# [H] CVE-2018-7417

## Summary
Severity: High
Advisory: CVE-2018-7417
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7417
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.12 and 2.4.0 to 2.4.4, the IPMI dissector could crash. This was addressed in epan/dissectors/packet-ipmi-picmg.c by adding support for crafted packets that lack an IPMI header.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=81216a176b25dd8a616e11808a951e141a467009
- http://www.securityfocus.com/bid/103156
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-12.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14409

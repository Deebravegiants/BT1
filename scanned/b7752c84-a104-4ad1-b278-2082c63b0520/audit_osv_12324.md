# [H] CVE-2018-11359

## Summary
Severity: High
Advisory: CVE-2018-11359
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11359
Type: osv

## Details
In Wireshark 2.6.0, 2.4.0 to 2.4.6, and 2.2.0 to 2.2.14, the RRC dissector and other dissectors could crash. This was addressed in epan/proto.c by avoiding a NULL pointer dereference.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=beaebe91b14564fb9f86f0726bab09927872721b
- http://www.securityfocus.com/bid/104308
- http://www.securitytracker.com/id/1041036
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-33.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14703

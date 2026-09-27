# [H] CVE-2018-14368

## Summary
Severity: High
Advisory: CVE-2018-14368
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14368
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.1, 2.4.0 to 2.4.7, and 2.2.0 to 2.2.15, the Bazaar protocol dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-bzr.c by properly handling items that are too long.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6c44312f465014eb409d766a9828b7f101f6251c
- http://www.securityfocus.com/bid/104847
- http://www.securitytracker.com/id/1041608
- https://lists.debian.org/debian-lts-announce/2018/07/msg00045.html
- https://www.wireshark.org/security/wnpa-sec-2018-40.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14841

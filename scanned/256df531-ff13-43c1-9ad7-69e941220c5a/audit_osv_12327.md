# [H] CVE-2018-11361

## Summary
Severity: High
Advisory: CVE-2018-11361
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11361
Type: osv

## Details
In Wireshark 2.6.0, the IEEE 802.11 protocol dissector could crash. This was addressed in epan/crypt/dot11decrypt.c by avoiding a buffer overflow during FTE processing in Dot11DecryptTDLSDeriveKey.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=1b52f9929238ce3948ec924ae4f9456b5e9df558
- http://www.securityfocus.com/bid/104308
- http://www.securitytracker.com/id/1041036
- https://www.wireshark.org/security/wnpa-sec-2018-32.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14686

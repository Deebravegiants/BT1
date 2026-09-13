# [H] CVE-2018-14342

## Summary
Severity: High
Advisory: CVE-2018-14342
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14342
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.1, 2.4.0 to 2.4.7, and 2.2.0 to 2.2.15, the BGP protocol dissector could go into a large loop. This was addressed in epan/dissectors/packet-bgp.c by validating Path Attribute lengths.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=36af43dbb7673495948cd65d0346e8b9812b941c
- http://www.securityfocus.com/bid/104847
- http://www.securitytracker.com/id/1041608
- https://lists.debian.org/debian-lts-announce/2018/07/msg00045.html
- https://www.wireshark.org/security/wnpa-sec-2018-34.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13741

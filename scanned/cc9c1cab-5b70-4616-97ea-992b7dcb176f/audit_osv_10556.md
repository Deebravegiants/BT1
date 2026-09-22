# [H] CVE-2017-17084

## Summary
Severity: High
Advisory: CVE-2017-17084
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/CVE-2017-17084
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.2 and 2.2.0 to 2.2.10, the IWARP_MPA dissector could crash. This was addressed in epan/dissectors/packet-iwarp-mpa.c by validating a ULPDU length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=8502fe94ef9e431860921507e1a351c5e3f5c634
- https://lists.debian.org/debian-lts-announce/2017/12/msg00029.html
- http://www.securityfocus.com/bid/102030
- https://www.debian.org/security/2017/dsa-4060
- https://www.wireshark.org/security/wnpa-sec-2017-47.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14236

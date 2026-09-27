# [H] CVE-2018-11357

## Summary
Severity: High
Advisory: CVE-2018-11357
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11357
Type: osv

## Details
In Wireshark 2.6.0, 2.4.0 to 2.4.6, and 2.2.0 to 2.2.14, the LTP dissector and other dissectors could consume excessive memory. This was addressed in epan/tvbuff.c by rejecting negative lengths.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=ab8a33ef083b9732c89117747a83a905a676faf6
- http://www.securityfocus.com/bid/104308
- http://www.securitytracker.com/id/1041036
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-28.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14678

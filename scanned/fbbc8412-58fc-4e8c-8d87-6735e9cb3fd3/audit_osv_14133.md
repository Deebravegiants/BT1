# [H] CVE-2018-7335

## Summary
Severity: High
Advisory: CVE-2018-7335
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7335
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, the IEEE 802.11 dissector could crash. This was addressed in epan/crypt/airpdcap.c by rejecting lengths that are too small.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a2901dcf45c9f1b07abfbf2a0b0cd654371d72a4
- http://www.securityfocus.com/bid/103165
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-05.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14442

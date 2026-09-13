# [H] CVE-2018-9260

## Summary
Severity: High
Advisory: CVE-2018-9260
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9260
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.5 and 2.2.0 to 2.2.13, the IEEE 802.15.4 dissector could crash. This was addressed in epan/dissectors/packet-ieee802154.c by ensuring that an allocation step occurs.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=14d6f717d8ea27688af48532edb1d29f502ea8f0
- https://lists.debian.org/debian-lts-announce/2018/05/msg00019.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-17.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14468

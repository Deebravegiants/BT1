# [H] CVE-2017-17997

## Summary
Severity: High
Advisory: CVE-2017-17997
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-30
Source: https://osv.dev/vulnerability/CVE-2017-17997
Type: osv

## Details
In Wireshark before 2.2.12, the MRDISC dissector misuses a NULL pointer and crashes. This was addressed in epan/dissectors/packet-mrdisc.c by validating an IPv4 address. This vulnerability is similar to CVE-2017-9343.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=80a695869c9aef2fb473d9361da068022be7cb50
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-02.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14299
- https://code.wireshark.org/review/#/c/25063/

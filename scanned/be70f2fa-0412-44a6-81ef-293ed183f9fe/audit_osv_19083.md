# [M] CVE-2020-7045

## Summary
Severity: Medium
Advisory: CVE-2020-7045
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-16
Source: https://osv.dev/vulnerability/CVE-2020-7045
Type: osv

## Details
In Wireshark 3.0.x before 3.0.8, the BT ATT dissector could crash. This was addressed in epan/dissectors/packet-btatt.c by validating opcodes.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=01f261de41f4dd3233ef578e5c0ffb9c25c7d14d
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://www.wireshark.org/security/wnpa-sec-2020-02.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16258

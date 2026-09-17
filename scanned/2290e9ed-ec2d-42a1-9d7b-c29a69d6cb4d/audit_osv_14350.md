# [H] CVE-2018-9258

## Summary
Severity: High
Advisory: CVE-2018-9258
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9258
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.5, the TCP dissector could crash. This was addressed in epan/dissectors/packet-tcp.c by preserving valid data sources.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2d4695de1477df60b0188fd581c0c279db601978
- https://lists.debian.org/debian-lts-announce/2018/05/msg00019.html
- https://www.wireshark.org/security/wnpa-sec-2018-21.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14472

# [H] CVE-2018-7334

## Summary
Severity: High
Advisory: CVE-2018-7334
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7334
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, the UMTS MAC dissector could crash. This was addressed in epan/dissectors/packet-umts_mac.c by rejecting a certain reserved value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=8ed705e1227d3d582e3f0de435bba606d053d686
- http://www.securityfocus.com/bid/103162
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-07.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14339

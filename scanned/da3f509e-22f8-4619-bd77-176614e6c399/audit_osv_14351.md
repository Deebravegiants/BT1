# [H] CVE-2018-9259

## Summary
Severity: High
Advisory: CVE-2018-9259
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9259
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.5 and 2.2.0 to 2.2.13, the MP4 dissector could crash. This was addressed in epan/dissectors/file-mp4.c by restricting the box recursion depth.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2113179835b37549f245ac7c05ff2b96276893e4
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-15.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13777

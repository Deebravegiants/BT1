# [H] CVE-2018-7336

## Summary
Severity: High
Advisory: CVE-2018-7336
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7336
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, the FCP protocol dissector could crash. This was addressed in epan/dissectors/packet-fcp.c by checking for a NULL pointer.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=b56f598f1bc04f5d00f13b38c713763928cedb7c
- http://www.securityfocus.com/bid/103166
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-09.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14374

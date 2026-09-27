# [H] CVE-2018-7337

## Summary
Severity: High
Advisory: CVE-2018-7337
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7337
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4, the DOCSIS protocol dissector could crash. This was addressed in plugins/docsis/packet-docsis.c by removing the recursive algorithm that had been used for concatenated PDUs.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=511a8b0b546d25413e289dc5a7d3a455a33994c2
- http://www.securityfocus.com/bid/103164
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://www.wireshark.org/security/wnpa-sec-2018-08.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14446

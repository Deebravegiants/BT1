# [H] CVE-2018-7332

## Summary
Severity: High
Advisory: CVE-2018-7332
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7332
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, epan/dissectors/packet-reload.c had an infinite loop that was addressed by validating a length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=1ab0585098c7ce20f3afceb6730427cc2a1e98ea
- http://www.securityfocus.com/bid/103158
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14445

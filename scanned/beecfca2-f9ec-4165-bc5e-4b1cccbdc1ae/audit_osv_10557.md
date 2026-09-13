# [H] CVE-2017-17085

## Summary
Severity: High
Advisory: CVE-2017-17085
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/CVE-2017-17085
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.2 and 2.2.0 to 2.2.10, the CIP Safety dissector could crash. This was addressed in epan/dissectors/packet-cipsafety.c by validating the packet length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f5939debe96e3c3953c6020818f1fbb80eb83ce8
- https://lists.debian.org/debian-lts-announce/2017/12/msg00029.html
- https://www.exploit-db.com/exploits/43233/
- http://www.securityfocus.com/bid/102071
- https://www.debian.org/security/2017/dsa-4060
- https://www.wireshark.org/security/wnpa-sec-2017-49.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14250

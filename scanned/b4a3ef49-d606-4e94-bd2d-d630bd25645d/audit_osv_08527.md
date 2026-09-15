# [M] CVE-2016-4078

## Summary
Severity: Medium
Advisory: CVE-2016-4078
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4078
Type: osv

## Details
The IEEE 802.11 dissector in Wireshark 1.12.x before 1.12.11 and 2.0.x before 2.0.3 does not properly restrict element lists, which allows remote attackers to cause a denial of service (deep recursion and application crash) via a crafted packet, related to epan/dissectors/packet-capwap.c and epan/dissectors/packet-ieee80211.c.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=e2745d741ec11f395d41c0aafa24df9dec136399
- http://www.wireshark.org/security/wnpa-sec-2016-21.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11824
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12187

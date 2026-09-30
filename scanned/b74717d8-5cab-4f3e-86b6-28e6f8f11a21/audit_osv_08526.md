# [M] CVE-2016-4077

## Summary
Severity: Medium
Advisory: CVE-2016-4077
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4077
Type: osv

## Details
epan/reassemble.c in TShark in Wireshark 2.0.x before 2.0.3 relies on incorrect special-case handling of truncated Tvb data structures, which allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=c5b2c1e8f40cee913bd70fcc00284483b3c92fcd
- http://www.wireshark.org/security/wnpa-sec-2016-20.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11799
- https://code.google.com/p/google-security-research/issues/detail?id=651

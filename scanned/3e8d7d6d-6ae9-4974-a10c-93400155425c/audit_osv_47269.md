# [H] CVE-2016-1983

## Summary
Severity: High
Advisory: CVE-2016-1983
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-01-27
Source: https://osv.dev/vulnerability/CVE-2016-1983
Type: osv

## Details
The client_host function in parsers.c in Privoxy before 3.0.24 allows remote attackers to cause a denial of service (invalid read and crash) via an empty HTTP Host header.

## References
- http://www.openwall.com/lists/oss-security/2016/01/22/3
- http://ijbswa.cvs.sourceforge.net/viewvc/ijbswa/current/parsers.c?r1=1.302&r2=1.303
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176475.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176492.html
- http://www.openwall.com/lists/oss-security/2016/01/21/4
- http://www.privoxy.org/announce.txt
- http://www.debian.org/security/2016/dsa-3460

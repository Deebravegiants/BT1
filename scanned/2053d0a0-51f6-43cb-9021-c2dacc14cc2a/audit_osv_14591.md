# [H] CVE-2019-10190

## Summary
Severity: High
Advisory: CVE-2019-10190
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/CVE-2019-10190
Type: osv

## Details
A vulnerability was discovered in DNS resolver component of knot resolver through version 3.2.0 before 4.1.0 which allows remote attackers to bypass DNSSEC validation for non-existence answer. NXDOMAIN answer would get passed through to the client even if its DNSSEC validation failed, instead of sending a SERVFAIL packet. Caching is not affected by this particular bug but see CVE-2019-10191.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMSSWBHINIX4WE6UDXWM66L7JYEK6XS6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZV5YZZ5766UIG2TFLFJL6EESQNAP5X5/
- https://www.knot-resolver.cz/2019-07-10-knot-resolver-4.1.0.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10190

# [C] CVE-2016-1245

## Summary
Severity: Critical
Advisory: CVE-2016-1245
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-22
Source: https://osv.dev/vulnerability/CVE-2016-1245
Type: osv

## Details
It was discovered that the zebra daemon in Quagga before 1.0.20161017 suffered from a stack-based buffer overflow when processing IPv6 Neighbor Discovery messages. The root cause was relying on BUFSIZ to be compatible with a message size; however, BUFSIZ is system-dependent.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0794.html
- http://www.gossamer-threads.com/lists/quagga/users/31952
- http://www.securityfocus.com/bid/93775
- https://security.gentoo.org/glsa/201701-48
- https://www.debian.org/security/2016/dsa-3695
- https://bugzilla.redhat.com/show_bug.cgi?id=1386109
- https://github.com/Quagga/quagga/commit/cfb1fae25f8c092e0d17073eaf7bd428ce1cd546

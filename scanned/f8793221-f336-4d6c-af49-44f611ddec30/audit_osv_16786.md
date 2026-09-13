# [M] CVE-2019-9741

## Summary
Severity: Medium
Advisory: CVE-2019-9741
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-03-13
Source: https://osv.dev/vulnerability/CVE-2019-9741
Type: osv

## Details
An issue was discovered in net/http in Go 1.11.5. CRLF injection is possible if the attacker controls a url parameter, as demonstrated by the second argument to http.NewRequest with \r\n followed by an HTTP header or a Redis command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TOOVCEPQM7TZA6VEZEEB7QZABXNHQEHH/
- http://www.securityfocus.com/bid/107432
- https://access.redhat.com/errata/RHSA-2019:1300
- https://access.redhat.com/errata/RHSA-2019:1519
- https://lists.debian.org/debian-lts-announce/2019/04/msg00007.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00015.html
- https://github.com/golang/go/issues/30794

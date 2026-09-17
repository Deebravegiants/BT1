# [M] CVE-2020-12272

## Summary
Severity: Medium
Advisory: CVE-2020-12272
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2020-12272
Type: osv

## Details
OpenDMARC through 1.3.2 and 1.4.x allows attacks that inject authentication results to provide false information about the domain that originated an e-mail message. This is caused by incorrect parsing and interpretation of SPF/DKIM authentication results, as demonstrated by the example.net(.example.com substring.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00035.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2D4JGHMALEJEWWG56DKR5OZB22TK7W5B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KBOGOQOK3TIWWJV66MW5YWNRJAFFYGR5/
- https://www.usenix.org/system/files/sec20fall_chen-jianjun_prepub_0.pdf
- https://sourceforge.net/p/opendmarc/tickets/237/

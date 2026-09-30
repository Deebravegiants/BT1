# [C] CVE-2019-20790

## Summary
Severity: Critical
Advisory: CVE-2019-20790
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2019-20790
Type: osv

## Details
OpenDMARC through 1.3.2 and 1.4.x, when used with pypolicyd-spf 2.0.2, allows attacks that bypass SPF and DMARC authentication in situations where the HELO field is inconsistent with the MAIL FROM field.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2D4JGHMALEJEWWG56DKR5OZB22TK7W5B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KBOGOQOK3TIWWJV66MW5YWNRJAFFYGR5/
- https://www.usenix.org/system/files/sec20fall_chen-jianjun_prepub_0.pdf
- https://bugs.launchpad.net/pypolicyd-spf/+bug/1838816
- https://sourceforge.net/p/opendmarc/tickets/235/

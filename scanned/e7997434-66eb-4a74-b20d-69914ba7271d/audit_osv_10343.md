# [M] CVE-2017-15042

## Summary
Severity: Medium
Advisory: CVE-2017-15042
Aliases: GO-2021-0178
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15042
Type: osv

## Details
An unintended cleartext issue exists in Go before 1.8.4 and 1.9.x before 1.9.1. RFC 4954 requires that, during SMTP, the PLAIN auth scheme must only be used on network connections secured with TLS. The original implementation of smtp.PlainAuth in Go 1.0 enforced this requirement, and it was documented to do so. In 2013, upstream issue #5184, this was changed so that the server may decide whether PLAIN is acceptable. The result is that if you set up a man-in-the-middle SMTP server that doesn't advertise STARTTLS and does advertise that PLAIN auth is OK, the smtp.PlainAuth implementation sends the username and password.

## References
- http://www.securityfocus.com/bid/101197
- https://access.redhat.com/errata/RHSA-2017:3463
- https://access.redhat.com/errata/RHSA-2018:0878
- https://golang.org/cl/68210
- https://groups.google.com/d/msg/golang-dev/RinSE3EiJBI/kYL7zb07AgAJ
- https://security.gentoo.org/glsa/201710-23
- https://github.com/golang/go/issues/22134
- https://golang.org/cl/68023

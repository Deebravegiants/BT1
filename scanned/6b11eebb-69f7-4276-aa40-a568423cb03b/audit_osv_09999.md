# [M] CVE-2017-12624

## Summary
Severity: Medium
Advisory: CVE-2017-12624
Aliases: GHSA-7vgj-8mw4-hg8r
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-14
Source: https://osv.dev/vulnerability/CVE-2017-12624
Type: osv

## Details
Apache CXF supports sending and receiving attachments via either the JAX-WS or JAX-RS specifications. It is possible to craft a message attachment header that could lead to a Denial of Service (DoS) attack on a CXF web service provider. Both JAX-WS and JAX-RS services are vulnerable to this attack. From Apache CXF 3.2.1 and 3.1.14, message attachment headers that are greater than 300 characters will be rejected by default. This value is configurable via the property "attachment-max-header-size".

## References
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4%40%3Ccommits.cxf.apache.org%3E
- http://www.securityfocus.com/bid/101859
- http://www.securitytracker.com/id/1040486
- https://access.redhat.com/errata/RHSA-2018:2423
- https://access.redhat.com/errata/RHSA-2018:2424
- https://access.redhat.com/errata/RHSA-2018:2425
- https://access.redhat.com/errata/RHSA-2018:2428
- http://cxf.apache.org/security-advisories.data/CVE-2017-12624.txt.asc

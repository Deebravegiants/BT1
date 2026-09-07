# [M] Improper Authentication in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-xf9f-32gh-h2w4
CVE: CVE-2012-5633
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xf9f-32gh-h2w4
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf` — affected >=0 <2.5.8
- Maven: `org.apache.cxf:cxf` — affected >=2.6.0 <2.6.5
- Maven: `org.apache.cxf:cxf` — affected >=2.7.0 <2.7.2

## Details
The URIMappingInterceptor in Apache CXF before 2.5.8, 2.6.x before 2.6.5, and 2.7.x before 2.7.2, when using the WSS4JInInterceptor, bypasses WS-Security processing, which allows remote attackers to obtain access to SOAP services via an HTTP GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5633
- https://github.com/apache/cxf/commit/0cbc56618b6048847debe670d54919e227744401
- https://github.com/apache/cxf/commit/1a6b532d53a7b98018871982049e4b0c80dc837c
- https://github.com/apache/cxf/commit/94a98b3fe9c79e2cf3941acbbad216ba54999bc0
- https://github.com/apache/cxf/commit/d99f96aa970d9f2faa8ed45e278a403af48757ae
- https://github.com/apache/cxf/commit/db11c9115f31e171de4622149f157d8283f6c720
- https://github.com/apache/cxf/commit/e0cdf873942b4d3fbc253e8ce6bb6fce3898019d
- https://github.com/apache/cxf/commit/e733c692e933a7f82424d3744aace9304cd5d4f6
- https://web.archive.org/web/20130216044418/http://www.securityfocus.com:80/bid/57874
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c%40%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E

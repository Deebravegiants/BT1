# [H] Session Fixation in Apache CXF

## Summary
Severity: High
Advisory: GHSA-v936-x3j5-c76j
CVE: CVE-2017-5656
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v936-x3j5-c76j
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=3.1.0 <3.1.11
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.0.13

## Details
Apache CXF's STSClient before 3.1.11 and 3.0.13 uses a flawed way of caching tokens that are associated with delegation tokens, which means that an attacker could craft a token which would return an identifer corresponding to a cached token for another user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5656
- https://github.com/apache/cxf/commit/1a4fe22fc297f8be204788bcdfcd498e91201a01
- https://access.redhat.com/errata/RHSA-2017:1832
- https://access.redhat.com/errata/RHSA-2018:1694
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2017-5656.txt.asc?version=1&modificationDate=1492515113282&api=v2
- http://www.securityfocus.com/bid/97971
- http://www.securitytracker.com/id/1038282

# [H] Improper Restriction of XML External Entity Reference in Apache CXF JAX-RS

## Summary
Severity: High
Advisory: GHSA-x7xf-253v-x3w8
CVE: CVE-2016-8739
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x7xf-253v-x3w8
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.0.12
- Maven: `org.apache.cxf:cxf-core` — affected >=3.1.0 <3.1.9

## Details
The JAX-RS module in Apache CXF prior to 3.0.12 and 3.1.x prior to 3.1.9 provides a number of Atom JAX-RS MessageBodyReaders. These readers use Apache Abdera Parser which expands XML entities by default which represents a major XXE risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8739
- https://github.com/apache/cxf/commit/8e4970d9
- https://github.com/apache/cxf/commit/9deb2d17
- https://access.redhat.com/errata/RHSA-2017:0868
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2016-8739.txt.asc

# [M] Missing XML Validation in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-254q-rp36-v2m8
CVE: CVE-2013-2160
CWE: CWE-112
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-254q-rp36-v2m8
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-frontend-jaxrs` — affected >=2.5.0 <2.5.10
- Maven: `org.apache.cxf:cxf-rt-frontend-jaxrs` — affected >=2.6.0 <2.6.7
- Maven: `org.apache.cxf:cxf-rt-frontend-jaxrs` — affected >=2.7.0 <2.7.4

## Details
The streaming XML parser in Apache CXF 2.5.x before 2.5.10, 2.6.x before 2.6.7, and 2.7.x before 2.7.4 allows remote attackers to cause a denial of service (CPU and memory consumption) via crafted XML with a large number of (1) elements, (2) attributes, (3) nested constructs, and possibly other vectors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2160
- https://bugzilla.redhat.com/show_bug.cgi?id=929197
- https://cxf.apache.org/security-advisories.data/CVE-2013-2160.txt.asc
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://jira.codehaus.org/browse/WSTX-285
- http://jira.codehaus.org/browse/WSTX-287
- http://rhn.redhat.com/errata/RHSA-2013-1028.html
- http://rhn.redhat.com/errata/RHSA-2013-1437.html

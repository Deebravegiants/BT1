# [M] Uncontrolled Resource Consumption in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-5xf9-3v63-ww6f
CVE: CVE-2014-0110
CWE: CWE-400
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5xf9-3v63-ww6f
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <2.6.14
- Maven: `org.apache.cxf:cxf-core` — affected >=2.7.0 <2.7.11

## Details
Apache CXF before 2.6.14 and 2.7.x before 2.7.11 allows remote attackers to cause a denial of service (/tmp disk consumption) via a large invalid SOAP message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0110
- https://github.com/apache/cxf/commit/35cd29270b77b489cb23552637d66d47ce480f4c
- https://github.com/apache/cxf/commit/643b1bc7320ca90c3e078e50509f9a30a0ab45be
- https://github.com/apache/cxf/commit/8f4799b5bc5ed0fe62d6e018c45d960e3652373e
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2014-0110.txt.asc
- http://rhn.redhat.com/errata/RHSA-2014-1351.html
- http://rhn.redhat.com/errata/RHSA-2015-0850.html
- http://rhn.redhat.com/errata/RHSA-2015-0851.html

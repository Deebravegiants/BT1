# [H] Covert Timing Channel in Apache CXF

## Summary
Severity: High
Advisory: GHSA-qc2p-q7x9-v64p
CVE: CVE-2017-3156
CWE: CWE-385
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qc2p-q7x9-v64p
Type: github-advisory

## Affected
- Maven: `org.apache.cxf.karaf:apache-cxf` — affected >=0 <3.0.13
- Maven: `org.apache.cxf.karaf:apache-cxf` — affected >=3.1.0 <3.1.10

## Details
The OAuth2 Hawk and JOSE MAC Validation code in Apache CXF prior to 3.0.13 and 3.1.x prior to 3.1.10 is not using a constant time MAC signature comparison algorithm which may be exploited by sophisticated timing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3156
- https://github.com/apache/cxf/commit/1338469
- https://github.com/apache/cxf/commit/555843f
- https://access.redhat.com/errata/RHSA-2017:1832
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2017-3156.txt.asc

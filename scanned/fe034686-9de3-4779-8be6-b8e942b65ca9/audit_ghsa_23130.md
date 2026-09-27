# [M] Improper Certificate Validation in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-hgg6-8x62-m9gf
CVE: CVE-2017-5653
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hgg6-8x62-m9gf
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=3.1.0 <3.1.11
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.0.13

## Details
JAX-RS XML Security streaming clients in Apache CXF before 3.1.11 and 3.0.13 do not validate that the service response was signed or encrypted, which allows remote attackers to spoof servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5653
- https://github.com/apache/cxf/commit/20d0fa3ec41c16c52b74dcc006f9d9ea212fa80f
- https://access.redhat.com/errata/RHSA-2017:1832
- https://github.com/apache/cxf
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2017-5653.txt.asc?version=1&modificationDate=1492515074710&api=v2

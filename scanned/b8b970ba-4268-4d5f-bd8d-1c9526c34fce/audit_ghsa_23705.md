# [H] Remote web-service operation execution in Apache CXF

## Summary
Severity: High
Advisory: GHSA-55j7-f5wf-43m4
CVE: CVE-2012-3451
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-55j7-f5wf-43m4
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf` — affected >=0 <2.4.9
- Maven: `org.apache.cxf:cxf` — affected >=2.5.0 <2.5.5
- Maven: `org.apache.cxf:cxf` — affected >=2.6.0 <2.6.2

## Details
Apache CXF before 2.4.9, 2.5.x before 2.5.5, and 2.6.x before 2.6.2 allows remote attackers to execute unintended web-service operations by sending a header with a SOAP Action String that is inconsistent with the message body.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3451
- https://github.com/apache/cxf/commit/7230648f96573820d5bfa82c92c637391b448897
- https://github.com/apache/cxf/commit/878fe37f0b09888a42005fedc725ce497b5a694a
- https://github.com/apache/cxf/commit/9c70abe28fbf2b4c4df0b93ed12295ea5a012554
- https://github.com/apache/cxf/commit/deeeaa95a861b355068ca6febc7aa02a4a8c51e5
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
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf%40%3Ccommits.cxf.apache.org%3E
- https://github.com/apache/cxf
- https://exchange.xforce.ibmcloud.com/vulnerabilities/78734
- https://bugzilla.redhat.com/show_bug.cgi?id=851896

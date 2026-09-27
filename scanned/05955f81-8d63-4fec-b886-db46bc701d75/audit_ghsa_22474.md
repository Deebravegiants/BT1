# [M] Loop with Unreachable Exit Condition in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-gw5j-77f9-v2g2
CVE: CVE-2014-3584
CWE: CWE-835
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gw5j-77f9-v2g2
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-frontend-jaxrs` — affected >=2.5.0 <2.6.11
- Maven: `org.apache.cxf:cxf-rt-frontend-jaxrs` — affected >=2.7.0 <2.7.8
- Maven: `org.apache.cxf:cxf-rt-frontend-jaxrs` — affected >=3.0.0 <3.0.1

## Details
The SamlHeaderInHandler in Apache CXF before 2.6.11, 2.7.x before 2.7.8, and 3.0.x before 3.0.1 allows remote attackers to cause a denial of service (infinite loop) via a crafted SAML token in the authorization header of a request to a JAX-RS service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3584
- https://github.com/apache/cxf/commit/0b3894f57388b9955f2c33b2295223f2835cd7b3
- https://github.com/apache/cxf/commit/47b127dbdb4a10d282be92f2ebbe646f8cf6b03e
- https://exchange.xforce.ibmcloud.com/vulnerabilities/97753
- https://github.com/apache/cxf
- https://issues.apache.org/jira/browse/CXF-5390
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2014-3584.txt.asc
- http://seclists.org/oss-sec/2014/q4/437

# [M] Apache CXF JMX Integration is vulnerable to a MITM attack

## Summary
Severity: Medium
Advisory: GHSA-ffm7-7r8g-77xm
CVE: CVE-2020-1954
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-ffm7-7r8g-77xm
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-management` — affected >=0 <3.2.13
- Maven: `org.apache.cxf:cxf-rt-management` — affected >=3.3.0 <3.3.6

## Details
Apache CXF has the ability to integrate with JMX by registering an `InstrumentationManager` extension with the CXF bus. If the `createMBServerConnectorFactory` property of the default `InstrumentationManagerImpl` is not disabled, then it is vulnerable to a man-in-the-middle (MITM) style attack. An attacker on the same host can connect to the registry and rebind the entry to another server, thus acting as a proxy to the original. They are then able to gain access to all of the information that is sent and received over JMX.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1954
- https://github.com/apache/cxf/commit/1cf4fed546904a4a2560f53a2a2391d834b4026c
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://security.netapp.com/advisory/ntap-20220210-0001
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://cxf.apache.org/security-advisories.data/CVE-2020-1954.txt.asc?version=1&modificationDate=1585730169000&api=v2

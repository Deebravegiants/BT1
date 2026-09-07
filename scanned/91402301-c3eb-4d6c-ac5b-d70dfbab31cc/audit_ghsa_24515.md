# [M] Improper Neutralization of Input During Web Page Generation in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-vw2c-5wph-v92r
CVE: CVE-2016-6812
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vw2c-5wph-v92r
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.0.12
- Maven: `org.apache.cxf:cxf-core` — affected >=3.1.0 <3.1.9

## Details
The HTTP transport module in Apache CXF prior to 3.0.12 and 3.1.x prior to 3.1.9 uses FormattedServiceListWriter to provide an HTML page which lists the names and absolute URL addresses of the available service endpoints. The module calculates the base URL using the current HttpServletRequest. The calculated base URL is used by FormattedServiceListWriter to build the service endpoint absolute URLs. If the unexpected matrix parameters have been injected into the request URL then these matrix parameters will find their way back to the client in the services list page which represents an XSS risk to the client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6812
- https://github.com/apache/cxf/commit/1be97cb13aef121b799b1be4d9793c0e8b925a12
- https://github.com/apache/cxf/commit/1f824d8039c7a42a4aa46f844e6c800e1143c7e7
- https://github.com/apache/cxf/commit/32e89366e2daa5670ac7a5c5c19f0bf9329a4c1e
- https://github.com/apache/cxf/commit/a30397b0
- https://access.redhat.com/errata/RHSA-2017:0868
- https://github.com/apache/cxf
- https://issues.apache.org/jira/browse/CXF-6216
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rc774278135816e7afc943dc9fc78eb0764f2c84a2b96470a0187315c@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- http://cxf.apache.org/security-advisories.data/CVE-2016-6812.txt.asc

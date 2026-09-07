# [M] Reflected Cross-Site Scripting in Apache CXF

## Summary
Severity: Medium
Advisory: GHSA-f93p-f762-vr53
CVE: CVE-2019-17573
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-f93p-f762-vr53
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:apache-cxf` — affected >=0 <3.2.12
- Maven: `org.apache.cxf:apache-cxf` — affected >=3.3.0 <3.3.5
- Maven: `org.apache.cxf:cxf` — affected >=0 <3.2.12
- Maven: `org.apache.cxf:cxf` — affected >=3.3.0 <3.3.5

## Details
By default, Apache CXF creates a /services page containing a listing of the available endpoint names and addresses. This webpage is vulnerable to a reflected Cross-Site Scripting (XSS) attack, which allows a malicious actor to inject javascript into the web page. Please note that the attack exploits a feature which is not typically not present in modern browsers, who remove dot segments before sending the request. However, Mobile applications may be vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17573
- https://github.com/apache/cxf/commit/a02e96ba1095596bef481919f16a90c5e80a92c8
- https://lists.apache.org/thread.html/r36e44ffc1a9b365327df62cdfaabe85b9a5637de102cea07d79b2dbf@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r51fdd73548290b2dfd0b48f7ab69bf9ae064dd100364cd8a15f0b3ec@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r51fdd73548290b2dfd0b48f7ab69bf9ae064dd100364cd8a15f0b3ec@%3Cdev.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r51fdd73548290b2dfd0b48f7ab69bf9ae064dd100364cd8a15f0b3ec@%3Cusers.cxf.apache.org%3E
- https://lists.apache.org/thread.html/r81a41a2915985d49bc3ea57dde2018b03584a863878a8532a89f993f@%3Cusers.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rd49aabd984ed540c8ff7916d4d79405f3fa311d2fdbcf9ed307839a6@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rec7160382badd3ef4ad017a22f64a266c7188b9ba71394f0d321e2d4@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rf3b50583fefce2810cbd37c3d358cbcd9a03e750005950bf54546194@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rfb87e0bf3995e7d560afeed750fac9329ff5f1ad49da365129b7f89e@%3Ccommits.cxf.apache.org%3E
- https://lists.apache.org/thread.html/rff42cfa5e7d75b7c1af0e37589140a8f1999e578a75738740b244bd4@%3Ccommits.cxf.apache.org%3E
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://cxf.apache.org/security-advisories.data/CVE-2019-17573.txt.asc?version=1&modificationDate=1579178542000&api=v2
- http://www.openwall.com/lists/oss-security/2020/11/12/2

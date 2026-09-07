# [C] Apache Shiro Authentication Bypass vulnerability

## Summary
Severity: Critical
Advisory: GHSA-45x9-q6vj-cqgq
CVE: CVE-2022-40664
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-45x9-q6vj-cqgq
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <1.10.0

## Details
Apache Shiro before 1.10.0, Authentication Bypass Vulnerability in Shiro when forwarding or including via RequestDispatcher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40664
- https://github.com/apache/shiro
- https://lists.apache.org/thread/loc2ktxng32xpy7lfwxto13k4lvnhjwg
- https://security.netapp.com/advisory/ntap-20221118-0005
- https://shiro.apache.org/blog/2022/10/10/2022/apache-shiro-1101-released.html
- http://www.openwall.com/lists/oss-security/2022/10/12/1
- http://www.openwall.com/lists/oss-security/2022/10/12/2
- http://www.openwall.com/lists/oss-security/2022/10/13/1

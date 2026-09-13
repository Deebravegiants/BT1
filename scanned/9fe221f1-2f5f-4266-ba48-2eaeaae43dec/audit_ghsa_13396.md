# [C] Path Traversal in Apache Shiro

## Summary
Severity: Critical
Advisory: GHSA-pmhc-2g4f-85cg
CVE: CVE-2023-34478
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-24
Source: https://github.com/advisories/GHSA-pmhc-2g4f-85cg
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-web` — affected >=0 <1.12.0
- Maven: `org.apache.shiro:shiro-web` — affected >=2.0.0-alpha-1 <2.0.0-alpha-3

## Details
Apache Shiro, before 1.12.0 or 2.0.0-alpha-3, may be susceptible to a path traversal attack that results in an authentication bypass when used together with APIs or other web frameworks that route requests based on non-normalized requests.

Mitigation: Update to Apache Shiro 1.12.0+ or 2.0.0-alpha-3+

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34478
- https://github.com/apache/shiro/commit/c3ede3f94efb442acb0795714a022c2c121d1da0
- https://github.com/apache/shiro
- https://lists.apache.org/thread/mbv26onkgw9o35rldh7vmq11wpv2t2qk
- https://security.netapp.com/advisory/ntap-20230915-0005
- http://www.openwall.com/lists/oss-security/2023/07/24/4

# [H] Improper authorization due to caching in Jenkins Role-based Authorization Strategy Plugin

## Summary
Severity: High
Advisory: GHSA-25g4-p347-x748
CVE: CVE-2020-2286
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-25g4-p347-x748
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:role-strategy` — affected >=2.12 <3.1

## Details
Role-based Authorization Strategy Plugin 2.12 and newer uses a cache to speed up permission lookups. Role-based Authorization Strategy Plugin 3.0 and earlier this cache is not invalidated properly when an administrator changes the permission configuration. This can result in permissions being granted long after the configuration was changed to no longer grant them. Role-based Authorization Strategy Plugin 3.1 properly invalidates the cache on configuration changes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2286
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-1767
- http://www.openwall.com/lists/oss-security/2020/10/08/5

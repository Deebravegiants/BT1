# [H] Disabled permissions granted by Jenkins Assembla Auth Plugin

## Summary
Severity: High
Advisory: GHSA-qf42-f5vf-6w99
CVE: CVE-2023-41945
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-qf42-f5vf-6w99
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:assembla-auth` — affected >=0

## Details
Jenkins Assembla Auth Plugin 1.14 and earlier does not verify that the permissions it grants are enabled, resulting in users with EDIT permissions to be granted Overall/Manage and Overall/SystemRead permissions, even if those permissions are disabled and should not be granted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41945
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3065
- http://www.openwall.com/lists/oss-security/2023/09/06/9

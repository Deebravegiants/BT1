# [M] Jenkins has a missing permission check, allowing users to obtain agent names

## Summary
Severity: Medium
Advisory: GHSA-67v4-38h7-9jjp
CVE: CVE-2025-59474
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-67v4-38h7-9jjp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.516.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.517 <2.528

## Details
Jenkins 2.527 and earlier, LTS 2.516.2 and earlier does not perform a permission check in the sidepanel of a page intentionally accessible to users lacking Overall/Read permission.

This allows attackers without Overall/Read permission to list agent names through its sidepanel executors widget.

Jenkins 2.528, LTS 2.516.3 removes the sidepanel from the affected view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59474
- https://www.jenkins.io/security/advisory/2025-09-17/#SECURITY-3594
- http://www.openwall.com/lists/oss-security/2025/09/17/1

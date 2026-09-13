# [M] Jenkins Subversion Partial Release Manager Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-mr9j-qqjh-67f2
CVE: CVE-2024-28159
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-mr9j-qqjh-67f2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:svn-partial-release-mgr` — affected >=0

## Details
A missing permission check in Jenkins Subversion Partial Release Manager Plugin 1.0.1 and earlier allows attackers with Item/Read permission to trigger a build.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28159
- https://github.com/jenkinsci/svn-partial-release-mgr-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3325
- http://www.openwall.com/lists/oss-security/2024/03/06/3

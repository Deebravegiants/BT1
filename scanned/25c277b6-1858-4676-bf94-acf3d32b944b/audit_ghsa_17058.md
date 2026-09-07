# [M] Jenkins Subversion Partial Release Manager Plugin vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-rv35-69ff-g9gv
CVE: CVE-2024-28158
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-rv35-69ff-g9gv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:svn-partial-release-mgr` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Subversion Partial Release Manager Plugin 1.0.1 and earlier allows attackers to trigger a build.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28158
- https://github.com/jenkinsci/svn-partial-release-mgr-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3325
- http://www.openwall.com/lists/oss-security/2024/03/06/3

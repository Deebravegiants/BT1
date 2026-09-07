# [M] Jenkins: Missing permission check allows unauthorized cancellation of queue items

## Summary
Severity: Medium
Advisory: GHSA-mw82-xcg6-gx79
CVE: CVE-2026-53438
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-mw82-xcg6-gx79
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568

## Details
A missing permission check in Jenkins 2.567 and earlier, LTS 2.555.2 and earlier allows attackers with Item/Cancel permission, but lacking Item/Read permission, to cancel queue items they do not have permission to view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53438
- https://github.com/jenkinsci/jenkins/commit/a154e1108f3170dc036ecbe6b2a89f164ff1554e
- https://github.com/jenkinsci/jenkins/commit/d22d0916148a430dd308760641539d06c0d8a184
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3712

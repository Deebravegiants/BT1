# [M] Jenkins Open Redirect via Relative Path Segments in Post-Login Redirect URL

## Summary
Severity: Medium
Advisory: GHSA-3rqh-hch3-jhpc
CVE: CVE-2026-53436
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-3rqh-hch3-jhpc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3

## Details
Jenkins 2.567 and earlier, LTS 2.555.2 and earlier improperly determines that a redirect URL after login is legitimately pointing to Jenkins when it contains relative path segments (`./` or `../`), allowing attackers to perform phishing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53436
- https://github.com/jenkinsci/jenkins/commit/8ef52891b07eb639b38271e4bab5dab3c0f10fda
- https://github.com/jenkinsci/jenkins/commit/b32f2f27a82ed187a34f55b05edcc4a83563d574
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3711+3755

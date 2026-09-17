# [M] Jenkins is missing a permission check on password fields

## Summary
Severity: Medium
Advisory: GHSA-p3f5-98cv-562j
CVE: CVE-2025-67636
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-p3f5-98cv-562j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.529 <2.541
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.528.3

## Details
A missing permission check in Jenkins 2.540 and earlier, LTS 2.528.2 and earlier allows attackers with View/Read permission to view encrypted password values in views.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67636
- https://github.com/jenkinsci/jenkins/commit/3ee7380c5e167fab865f58b52a81ef01c24b9eb2
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-1809

# [H] Jenkins has a Denial of service vulnerability in HTTP-based CLI

## Summary
Severity: High
Advisory: GHSA-9p56-p6mw-w8qc
CVE: CVE-2025-67635
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-9p56-p6mw-w8qc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.529 <2.541
- Maven: `org.jenkins-ci.main:cli` — affected >=2.529 <2.541
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.528.3
- Maven: `org.jenkins-ci.main:cli` — affected >=0 <2.528.3

## Details
Jenkins 2.540 and earlier, LTS 2.528.2 and earlier does not properly close HTTP-based CLI connections when the connection stream becomes corrupted, allowing unauthenticated attackers to cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67635
- https://github.com/jenkinsci/jenkins/commit/efa1816322026f2b9235a27eee814bcc7ba0a764
- https://fluidattacks.com/blog/unauth-dos-in-jenkins-cli
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-3630

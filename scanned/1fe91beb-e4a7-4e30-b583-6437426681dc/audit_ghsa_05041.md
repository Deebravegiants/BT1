# [M] Jenkins: Open Redirect phishing attacks possible via "from" parameter in "Delegate to servlet container"

## Summary
Severity: Medium
Advisory: GHSA-92m7-4fpw-2wxm
CVE: CVE-2026-53440
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-92m7-4fpw-2wxm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.555.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.556 <2.568

## Details
Jenkins 2.567 and earlier, LTS 2.555.2 and earlier does not ensure that the "from" parameter in the "Delegate to servlet container" security realm is safe to redirect to after login, allowing attackers to perform phishing attacks by redirecting users to an attacker-controlled domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-53440
- https://github.com/jenkinsci/jenkins/commit/38071826c9a2113e1104714595262827a87b392f
- https://github.com/jenkinsci/jenkins/commit/c45e93f2d77d94ea3b0545eb5aca32b808a27586
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2026-06-10/#SECURITY-3721

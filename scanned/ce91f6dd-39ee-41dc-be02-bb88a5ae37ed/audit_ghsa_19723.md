# [M] Jenkins cross-site request forgery (CSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7g95-jmg9-h524
CVE: CVE-2025-27624
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-03-06
Source: https://github.com/advisories/GHSA-7g95-jmg9-h524
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.493 <2.500
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.492.2

## Details
Jenkins 2.499 and earlier, LTS 2.492.1 and earlier does not require POST requests for the HTTP endpoint toggling collapsed/expanded status of sidepanel widgets (e.g., Build Queue and Build Executor Status widgets), resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to have users toggle their collapsed/expanded status of sidepanel widgets.

Additionally, as the API accepts any string as the identifier of the panel ID to be toggled, attacker-controlled content can be stored in the victim’s user profile in Jenkins.

Jenkins 2.500, LTS 2.492.2 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27624
- https://github.com/jenkinsci/jenkins/commit/84ef1a4d4db17d0ce66522d0141f6e52e2a4c97c
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-03-05/#SECURITY-3498

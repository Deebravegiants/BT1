# [M] Jenkins CI Game Plugin allows Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-3qxr-q72q-hmwp
CVE: CVE-2012-4441
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-3qxr-q72q-hmwp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ci-game` — affected >=0 <1.19

## Details
Cross-site Scripting (XSS) in Jenkins main before 1.482 and LTS before 1.466.2 allows remote attackers to inject arbitrary web script or HTML in the CI game plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4441
- https://github.com/jenkinsci/ci-game-plugin/commit/9ef03da36524038322a7b9c14370a4c497e708f8
- https://github.com/jenkinsci/ci-game-plugin
- https://security-tracker.debian.org/tracker/CVE-2012-4441
- https://www.cloudbees.com/jenkins-security-advisory-2012-09-17
- http://www.openwall.com/lists/oss-security/2012/09/21/2

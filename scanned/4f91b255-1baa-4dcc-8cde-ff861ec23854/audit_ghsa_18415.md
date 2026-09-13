# [M] Jenkins Dead Man's Snitch Plugin vulnerability does not mask tokens

## Summary
Severity: Medium
Advisory: GHSA-m248-72rh-cpx4
CVE: CVE-2025-53667
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-m248-72rh-cpx4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:deadmanssnitch` — affected >=0

## Details
Jenkins Dead Man's Snitch Plugin 0.1 does not mask Dead Man's Snitch tokens displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53667
- https://github.com/jenkinsci/deadmanssnitch-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3524
- http://www.openwall.com/lists/oss-security/2025/07/09/4

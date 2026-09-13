# [M] Jenkins VAddy Plugin vulnerability exposes plaintext keys on its job configuration form

## Summary
Severity: Medium
Advisory: GHSA-8gp3-m447-gw2v
CVE: CVE-2025-53669
CWE: CWE-256
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-8gp3-m447-gw2v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vaddy-plugin` — affected >=0

## Details
Jenkins VAddy Plugin 1.2.8 and earlier does not mask Vaddy API Auth Keys displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53669
- https://github.com/jenkinsci/vaddy-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3527
- http://www.openwall.com/lists/oss-security/2025/07/09/4

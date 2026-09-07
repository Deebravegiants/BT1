# [M] Jenkins Xooa Plugin vulnerability does not mask its Xooa Deployment Token

## Summary
Severity: Medium
Advisory: GHSA-23j7-px3w-jwp2
CVE: CVE-2025-53677
CWE: CWE-256
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-23j7-px3w-jwp2
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:xooa` — affected >=0

## Details
Jenkins Xooa Plugin 0.0.7 and earlier does not mask the Xooa Deployment Token on the global configuration form, increasing the potential for attackers to observe and capture it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53677
- https://github.com/jenkinsci/xooa-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3522
- http://www.openwall.com/lists/oss-security/2025/07/09/4

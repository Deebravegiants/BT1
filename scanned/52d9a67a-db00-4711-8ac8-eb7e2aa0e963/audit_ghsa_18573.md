# [M] Jenkins Xooa Plugin vulnerability exposes unencrypted tokens to authenticated users

## Summary
Severity: Medium
Advisory: GHSA-56h7-r62c-83qp
CVE: CVE-2025-53676
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-56h7-r62c-83qp
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:xooa` — affected >=0

## Details
Jenkins Xooa Plugin 0.0.7 and earlier stores the Xooa Deployment Token unencrypted in its global configuration file on the Jenkins controller, where it can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53676
- https://github.com/jenkinsci/xooa-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3522
- http://www.openwall.com/lists/oss-security/2025/07/09/4

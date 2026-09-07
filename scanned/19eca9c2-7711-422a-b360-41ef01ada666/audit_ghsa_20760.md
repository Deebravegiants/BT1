# [M] Jenkins extreme-feedback Plugin vulnerable to Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-mrf6-4gw6-65v3
CVE: CVE-2022-41242
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-mrf6-4gw6-65v3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:extreme-feedback` — affected >=0

## Details
Jenkins extreme-feedback Plugin 1.7 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to discover information about job names attached to lamps, discover MAC and IP addresses of existing lamps, and rename lamps.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41242
- https://github.com/jenkinsci/extreme-feedback-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2001

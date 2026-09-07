# [M] Jenkins Start Windocks Containers Plugin vulnerable to cross-site request forgery

## Summary
Severity: Medium
Advisory: GHSA-6mgr-3374-4p3c
CVE: CVE-2025-64138
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-6mgr-3374-4p3c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:windocks-start-container` — affected >=0

## Details
Jenkins Start Windocks Containers Plugin 1.4 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

Additionally, this endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64138
- https://github.com/jenkinsci/windocks-start-container-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3531
- http://www.openwall.com/lists/oss-security/2025/10/29/2

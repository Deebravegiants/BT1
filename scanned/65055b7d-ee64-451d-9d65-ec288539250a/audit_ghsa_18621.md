# [M] Jenkins Themis Plugin vulnerable to cross-site request forgery

## Summary
Severity: Medium
Advisory: GHSA-93mh-mx9w-m69q
CVE: CVE-2025-64136
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-93mh-mx9w-m69q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:themis` — affected >=0

## Details
Jenkins Themis Plugin 1.4.1 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

Additionally, this endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64136
- https://github.com/jenkinsci/themis-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3517
- http://www.openwall.com/lists/oss-security/2025/10/29/2

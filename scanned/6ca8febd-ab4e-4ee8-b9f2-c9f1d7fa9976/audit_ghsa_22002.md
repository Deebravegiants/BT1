# [H] CSRF vulnerability in Jenkins autonomiq plugin

## Summary
Severity: High
Advisory: GHSA-g5wh-fw4m-2v28
CVE: CVE-2022-25194
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-g5wh-fw4m-2v28
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:autonomiq` — affected >=0 <1.16

## Details
Jenkins autonomiq Plugin 1.15 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified username and password.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25194
- https://github.com/jenkinsci/autonomiq-plugin/commit/e06b1ff67664a90819c9561bbc12f4c6e593d1dc
- https://github.com/jenkinsci/autonomiq-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2545

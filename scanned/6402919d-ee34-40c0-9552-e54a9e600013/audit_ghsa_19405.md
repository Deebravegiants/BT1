# [M] Jenkins Simple Queue Plugin Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-hcfh-qjcp-34q9
CVE: CVE-2025-31723
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-02
Source: https://github.com/advisories/GHSA-hcfh-qjcp-34q9
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:simple-queue` — affected >=0 <1.4.7

## Details
Jenkins Simple Queue Plugin 1.4.6 and earlier does not require POST requests for multiple HTTP endpoints, resulting in cross-site request forgery (CSRF) vulnerabilities.

These vulnerabilities allow attackers to change and reset the build queue order.

Simple Queue Plugin 1.4.7 requires POST requests for the affected HTTP endpoints.

Administrators can enable equivalent HTTP endpoints without CSRF protection via the global configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31723
- https://github.com/jenkinsci/simple-queue-plugin/commit/c1094666dcd139830620d6d1c21b13f847601e74
- https://github.com/jenkinsci/simple-queue-plugin
- https://www.jenkins.io/security/advisory/2025-04-02/#SECURITY-3469

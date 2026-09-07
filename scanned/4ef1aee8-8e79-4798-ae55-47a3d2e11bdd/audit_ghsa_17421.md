# [H] Jenkins Coverage Plugin has a stored cross-site scripting (XSS) vulnerability

## Summary
Severity: High
Advisory: GHSA-v3f3-rf6r-43x5
CVE: CVE-2025-67641
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-v3f3-rf6r-43x5
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:coverage` — affected >=0 <2.3056

## Details
Jenkins Coverage Plugin 2.3054.ve1ff7b_a_a_123b_ and earlier does not validate the configured coverage results ID when creating coverage results, only when submitting the job configuration through the UI, allowing attackers with Item/Configure permission to use a `javascript:` scheme URL as identifier by configuring the job through the REST API, resulting in a stored cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67641
- https://github.com/jenkinsci/coverage-plugin/commit/1dfe888b02499d39185397862cf2790efc03e955
- https://github.com/jenkinsci/coverage-plugin
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-3611

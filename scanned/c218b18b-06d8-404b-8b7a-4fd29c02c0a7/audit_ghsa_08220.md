# [M] Jenkins AppSpider Plugin does not perform a permission check in a method implementing form validation

## Summary
Severity: Medium
Advisory: GHSA-9wm7-8qf3-9v98
CVE: CVE-2026-48923
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-9wm7-8qf3-9v98
Type: github-advisory

## Affected
- Maven: `com.rapid7:jenkinsci-appspider-plugin` — affected >=0 <1.0.18

## Details
Jenkins AppSpider Plugin 1.0.17 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

AppSpider Plugin 1.0.18 requires Overall/Administer permission to use the affected method implementing form validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48923
- https://github.com/rapid7/jenkinsci-appspider-plugin
- https://www.jenkins.io/security/advisory/2026-05-27/#SECURITY-3671

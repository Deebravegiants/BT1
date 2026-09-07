# [M] Qualys Jenkins Plugin for Policy Compliance Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rwf9-8fqr-p44m
CVE: CVE-2023-6148
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-rwf9-8fqr-p44m
Type: github-advisory

## Affected
- Maven: `com.qualys.plugins:qualys-pc` — affected >=0 <1.0.6

## Details
Qualys Jenkins Plugin for Policy Compliance prior to version and including 1.0.5 was identified to be affected by a security flaw, which was missing a permission check while performing a connectivity check to Qualys Cloud Services. This allowed any user with login access and access to configure or edit jobs to utilize the plugin to configure a potential rouge endpoint via which it was possible to control response for certain request which could be injected with XSS payloads leading to XSS while processing the response data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6148
- https://github.com/jenkinsci/qualys-pc-plugin
- https://www.qualys.com/security-advisories
- https://www.qualys.com/security-advisories/cve-2023-6148
- http://www.openwall.com/lists/oss-security/2024/01/24/6

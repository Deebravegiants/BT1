# [M] Qualys Jenkins Plugin for WAS XML External Entity vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5gwh-r76w-934h
CVE: CVE-2023-6149
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-5gwh-r76w-934h
Type: github-advisory

## Affected
- Maven: `com.qualys.plugins:qualys-was` — affected >=0 <2.0.12

## Details
Qualys Jenkins Plugin for WAS prior to version and including 2.0.11 was identified to be affected by a security flaw, which was missing a permission check while performing a connectivity check to Qualys Cloud Services. This allowed any user with login access to configure or edit jobs to utilize the plugin and configure potential a rouge endpoint via which it was possible to control response for certain request which could be injected with XXE payloads leading to XXE while processing the response data

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6149
- https://github.com/jenkinsci/qualys-was-plugin/commit/b4eeb34747fa1b934abbdf686102f6495fdb02ee
- https://github.com/jenkinsci/qualys-was-plugin
- https://www.qualys.com/security-advisories
- https://www.qualys.com/security-advisories/cve-2023-6149

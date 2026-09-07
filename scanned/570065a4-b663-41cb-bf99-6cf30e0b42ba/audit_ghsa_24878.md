# [M] MunkiReport Managed Installs module Reflected Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-79xr-v794-wq35
CVE: CVE-2020-15883
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-79xr-v794-wq35
Type: github-advisory

## Affected
- Packagist: `munkireport/managedinstalls` — affected >=0 <2.6

## Details
A Cross-Site Scripting (XSS) vulnerability in the managedinstalls module before 2.6 for MunkiReport allows remote attackers to inject arbitrary web script or HTML via the last two URL parameters (through which installed packages names and versions are reported).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15883
- https://github.com/munkireport/managedinstalls/commit/708f6a2abc4b80a3751bcc9cf896f80d84250c55
- https://github.com/munkireport/managedinstalls
- https://github.com/munkireport/managedinstalls/releases/tag/v2.6
- https://github.com/munkireport/munkireport-php
- https://github.com/munkireport/munkireport-php/releases/tag/v5.6.3
- https://github.com/munkireport/munkireport-php/wiki/20200722-Reflected-XSS-In-Managedinstalls-Module

# [C] Incorrect Access Control in Ignition

## Summary
Severity: Critical
Advisory: GHSA-vhrp-8qx4-vr6c
CVE: CVE-2021-43996
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-vhrp-8qx4-vr6c
Type: github-advisory

## Affected
- Packagist: `facade/ignition` — affected >=0 <1.16.15
- Packagist: `facade/ignition` — affected >=2.0.0 <2.0.6

## Details
The Ignition component before 1.16.15, and 2.0.x before 2.0.6, for Laravel has a "fix variable names" feature that can lead to incorrect access control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43996
- https://github.com/facade/ignition/pull/285
- https://github.com/facade/ignition
- https://github.com/facade/ignition/compare/1.16.14...1.16.15
- https://github.com/facade/ignition/compare/2.0.5...2.0.6

# [M] Laravel has a File Validation Bypass

## Summary
Severity: Medium
Advisory: GHSA-78fx-h6xr-vch4
CVE: CVE-2025-27515
CWE: CWE-155
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-78fx-h6xr-vch4
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=12.0.0 <12.1.1
- Packagist: `laravel/framework` — affected >=11.0.0 <11.44.1
- Packagist: `laravel/framework` — affected >=0 <10.48.29

## Details
When using wildcard validation to validate a given file or image field array (`files.*`), a user-crafted malicious request could potentially bypass the validation rules.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-78fx-h6xr-vch4
- https://nvd.nist.gov/vuln/detail/CVE-2025-27515
- https://github.com/laravel/framework/commit/2d133034fefddfb047838f4caca3687a3ba811a5
- https://github.com/laravel/framework/commit/a4f7a8f9b83e21882abeef78c3174c66b0f4a26b
- https://github.com/laravel/framework

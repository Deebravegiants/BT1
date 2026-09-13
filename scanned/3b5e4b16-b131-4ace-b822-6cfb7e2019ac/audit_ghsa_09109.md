# [C] Scramble vulnerable to remote code execution via evaluation of user-controlled input in validation rules

## Summary
Severity: Critical
Advisory: GHSA-4rm2-28vj-fj39
CVE: CVE-2026-44262
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-4rm2-28vj-fj39
Type: github-advisory

## Affected
- Packagist: `dedoc/scramble` — affected >=0.13.2 <0.13.22

## Details
### Impact

A remote code execution (RCE) vulnerability affects versions `0.13.2` through `0.13.21`. When documentation endpoints are publicly accessible and validation rules reference user-controlled input, request supplied data may be evaluated during documentation generation, leading to execution of arbitrary PHP code in the application context.

### Patches

Fixed in version `0.13.22`.

### Workarounds

If upgrading is not immediately possible:

* Restrict access to documentation endpoints (`/docs/api`, `/docs/api.json`)
* Avoid using user-controlled variables inside validation rule expressions (e.g., values derived from request input)
* Disable documentation endpoints in production environments if not required

These measures significantly reduce or prevent exploitability.

## References
- https://github.com/dedoc/scramble/security/advisories/GHSA-4rm2-28vj-fj39
- https://nvd.nist.gov/vuln/detail/CVE-2026-44262
- https://github.com/dedoc/scramble
- https://github.com/dedoc/scramble/releases/tag/v0.13.22

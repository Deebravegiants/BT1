# [H] zenstruck/collection passing callable string to EntityRepository::find() and query()

## Summary
Severity: High
Advisory: GHSA-7xr2-8ff7-6fjq
CVE: CVE-2023-37473
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-14
Source: https://github.com/advisories/GHSA-7xr2-8ff7-6fjq
Type: github-advisory

## Affected
- Packagist: `zenstruck/collection` — affected >=0 <0.2.1

## Details
### Impact
Passing _callable strings_ (ie `system`) caused the function to be executed.

### Patches
Fixed in [v0.2.1](https://github.com/zenstruck/collection/releases/tag/v0.2.1).

### Workarounds
Do not allow passing user strings to `EntityRepository::find()` or `query()`.

### References
[Fix commit](https://github.com/zenstruck/collection/commit/f4b1c488206e1b1581b06fcd331686846f13f19c).

## References
- https://github.com/zenstruck/collection/security/advisories/GHSA-7xr2-8ff7-6fjq
- https://nvd.nist.gov/vuln/detail/CVE-2023-37473
- https://github.com/zenstruck/collection/commit/f4b1c488206e1b1581b06fcd331686846f13f19c
- https://github.com/zenstruck/collection
- https://github.com/zenstruck/collection/releases/tag/v0.2.1

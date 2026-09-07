# [M] Cross-site Scripting in kimai2

## Summary
Severity: Medium
Advisory: GHSA-427q-jp8v-ww95
CVE: CVE-2021-3976
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-427q-jp8v-ww95
Type: github-advisory

## Affected
- Packagist: `kevinpapst/kimai2` — affected >=0 <1.16.2

## Details
CSRF related to duplicate action. (the duplication occurs first before redirecting to edit form). This vulnerability is capable of tricking admin users to duplicate teams.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3976
- https://github.com/kevinpapst/kimai2/commit/b28e9c120c87222e21a238f1b03a609d6a5d506e
- https://huntr.dev/bounties/0567048a-118c-42ec-9f94-b55533017406

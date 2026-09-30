# [M] Snipe-IT's import created_by can be overwritten

## Summary
Severity: Medium
Advisory: GHSA-5wx7-xq8j-v4qm
CVE: CVE-2026-55475
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-5wx7-xq8j-v4qm
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.1

## Details
### Impact
The `created_by` of an import file can be arbitrarily overwritten via the Importer API endpoint by a user with CSV import capabilities who also has a valid API key.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-5wx7-xq8j-v4qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-55475
- https://github.com/grokability/snipe-it/pull/19072
- https://github.com/grokability/snipe-it/commit/39fbe983132feca2ef15c1c0200fcc77c23a1434
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.1

# [M] Statamic: Missing authorization on navigation endpoint allows disclosure of restricted entries

## Summary
Severity: Medium
Advisory: GHSA-qh8c-7588-qfrv
CVE: CVE-2026-64662
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-qh8c-7588-qfrv
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.74.1
- Packagist: `statamic/cms` — affected >=6.0.0 <6.24.0

## Details
### Impact

An authenticated Control Panel user could view content from entries they don't have permission to view, including entry content and custom field values, from any collection and including unpublished entries. No data could be modified.

### Patches

This has been fixed in 5.74.1 and 6.24.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-qh8c-7588-qfrv
- https://github.com/statamic/cms/pull/14906
- https://github.com/statamic/cms/commit/6557f1d8a0d61c0e7ad9c9a8f42cb3288607495d
- https://github.com/statamic/cms
- https://github.com/statamic/cms/releases/tag/v5.74.1
- https://github.com/statamic/cms/releases/tag/v6.24.0

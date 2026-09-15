# [M] Statamic CMS: Missing authorization on Control Panel fieldtype endpoints allows disclosure of restricted resources

## Summary
Severity: Medium
Advisory: GHSA-2497-6pwj-pwg7
CVE: CVE-2026-49288
CWE: CWE-200, CWE-862, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-2497-6pwj-pwg7
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.23
- Packagist: `statamic/cms` — affected >=6.0.0 <6.20.0

## Details
### Impact

An authenticated Control Panel user could view metadata and content for resources they don't have permission to view, including entries, assets, users, roles, groups, and other configured resources. Depending on the resource, this could expose titles, custom field values, entry content, asset metadata, and the existence of users, roles, and groups. No data could be modified.

### Patches

This has been fixed in 5.73.23 and 6.20.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-2497-6pwj-pwg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-49288
- https://github.com/statamic/cms

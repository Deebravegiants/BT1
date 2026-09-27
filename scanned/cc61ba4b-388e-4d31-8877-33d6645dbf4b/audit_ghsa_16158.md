# [M] Statamic CMS has a Path Traversal in Asset Upload

## Summary
Severity: Medium
Advisory: GHSA-p7f6-8mcm-fwv3
CVE: CVE-2024-52600
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-11-19
Source: https://github.com/advisories/GHSA-p7f6-8mcm-fwv3
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.17.0

## Details
Assets uploaded with appropriately crafted filenames may result in them being placed in a location different than what was configured.

### Impact

- Affects front-end forms with `assets` fields.
- Affects other places where assets can be uploaded, although users would need upload permissions anyway.
- Files can be uploaded so they would be located on the server in a different location, and potentially override existing files.
- Traversal _outside_ an asset container was not possible.

### Patches

This has been fixed in 5.17.0.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-p7f6-8mcm-fwv3
- https://nvd.nist.gov/vuln/detail/CVE-2024-52600
- https://github.com/statamic/cms/commit/0c07c10009a2439c8ee56c8faefd1319dc6e388d
- https://github.com/statamic/cms/commit/400875b20f40e1343699d536a432a6fc284346da
- https://github.com/statamic/cms/commit/4cc2c9bd0f39a93b3fc7e9ef0f12792576fd380d
- https://github.com/statamic/cms

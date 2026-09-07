# [M] Statamic allows unauthorized content access through missing authorization in its revision controllers 

## Summary
Severity: Medium
Advisory: GHSA-4hp7-3wxg-cv9q
CVE: CVE-2026-33887
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-4hp7-3wxg-cv9q
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=0 <5.73.16
- Packagist: `statamic/cms` — affected >=6.0.0-alpha.1 <6.7.2

## Details
### Impact
Authenticated Control Panel users could view entry revisions for any collection with revisions enabled, regardless of whether they had the required collection permissions. This bypasses the authorization checks that the main entry controllers enforce, exposing entry field values and blueprint data.

Users could also create entry revisions without edit permission, though this only snapshots the existing content state and does not affect published content.

### Patches
This has been fixed in 5.73.16 and 6.7.2.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-4hp7-3wxg-cv9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-33887
- https://github.com/statamic/cms

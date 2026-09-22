# [M] Capgo - Deleted Bundle Selection via Missing Deletion Filter in /updates Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-56314
Aliases: GHSA-hqq2-87cp-j83x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56314
Type: osv

## Details
Capgo before 12.128.12 fails to filter deleted app versions when joining channels during /updates resolution, allowing deleted bundles to remain selectable. Attackers can continue deploying deleted bundles to devices by exploiting the missing app_versions.deleted filter in channel version joins.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56314.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-hqq2-87cp-j83x
- https://nvd.nist.gov/vuln/detail/CVE-2026-56314
- https://www.vulncheck.com/advisories/capgo-deleted-bundle-selection-via-missing-deletion-filter-in-updates-endpoint

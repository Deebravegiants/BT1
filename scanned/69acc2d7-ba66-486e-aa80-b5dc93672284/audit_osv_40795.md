# [M] Snipe-IT: Path traversal vulnerability via CSV import `image` field

## Summary
Severity: Medium
Advisory: CVE-2026-55469
Aliases: GHSA-xr9m-gphc-9p63
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55469
Type: osv

## Details
Snipe-IT is an IT asset/license management system. Prior to 8.6.2, an authenticated user with import and assets.update permissions can place a path traversal string in an asset image field through CSV import and then trigger image deletion, allowing deletion of arbitrary files accessible to the server process. This issue is fixed in version 8.6.2.

## References
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55469.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-xr9m-gphc-9p63
- https://nvd.nist.gov/vuln/detail/CVE-2026-55469
- https://github.com/grokability/snipe-it/commit/abc4363e8393b29a5566b8c50144426af72bbc97

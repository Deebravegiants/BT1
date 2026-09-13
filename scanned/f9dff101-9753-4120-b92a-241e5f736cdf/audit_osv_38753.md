# [M] novaGallery: Unauthenticated Path Traversal in Album and Cached Image Routes Allows Reading Images Outside Gallery Root

## Summary
Severity: Medium
Advisory: CVE-2026-42028
Aliases: GHSA-wv5j-98c7-frm9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42028
Type: osv

## Details
novaGallery is a php image gallery. Prior to version 2.1.1, a path traversal vulnerability has been identified in novaGallery. This allows unauthenticated users to read image files outside the intended gallery root directory. This issue has been patched in version 2.1.1.

## References
- https://github.com/novafacile/novagallery/releases/tag/v2.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42028.json
- https://github.com/novafacile/novagallery/security/advisories/GHSA-wv5j-98c7-frm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42028
- https://github.com/novafacile/novagallery/commit/46fe7b0f79f429e18c8cff3f92360c4513732ba6

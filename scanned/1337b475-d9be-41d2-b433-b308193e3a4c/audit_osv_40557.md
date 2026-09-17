# [H] FileWiki has path traversal in RenameAsset via unsanitized oldFilename parameter

## Summary
Severity: High
Advisory: CVE-2026-53528
Aliases: GHSA-g2wp-jm5c-jqfj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53528
Type: osv

## Details
LeafWiki is a self-hosted wiki. Versions 0.3.0 through 0.10.0 have a path traversal vulnerability in LeafWiki’s asset rename functionality. An authenticated user with editor permissions could move files that are accessible to the LeafWiki server process into a page’s asset directory. This could allow sensitive local files, such as the application database, to become downloadable as page assets. Users should update to version 0.10.1 or greater. As an additional mitigation, operators should ensure that the LeafWiki process runs with the least privileges necessary and does not have filesystem access to sensitive files outside the application’s required directories. Until a patch is applied, operators may reduce risk by restricting editor access to trusted users only and by limiting the filesystem permissions of the LeafWiki process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53528.json
- https://github.com/perber/leafwiki/security/advisories/GHSA-g2wp-jm5c-jqfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-53528

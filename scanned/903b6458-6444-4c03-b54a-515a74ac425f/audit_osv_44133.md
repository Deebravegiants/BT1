# [M] LeafWiki 0.10.0 through 0.12.0 Uncontrolled Resource Consumption via Unbounded ZIP Extraction

## Summary
Severity: Medium
Advisory: CVE-2026-80189
Aliases: GHSA-258m-crqp-25xc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80189
Type: osv

## Details
LeafWiki extracts an uploaded ZIP archive without limiting how much data it will write. ZipExtractor.ExtractToDir in internal/importer/zip_extractor.go opens each entry and copies it to the destination with io.Copy, which runs to the end of the decompressed stream, so only the size of the uploaded archive is bounded and the size it expands to is not. The import route that reaches this code requires the Editor or Admin role, and the upload itself is capped at 500 MiB compressed. Because a ZIP entry can compress at a very high ratio, an archive well inside that cap can expand to hundreds of gigabytes as it is written out. The extraction directory defaults to a location under the operating system temporary directory, so the written data consumes the disk backing that path, which on a tmpfs-backed temporary directory is memory. A user holding the Editor role can therefore exhaust the storage the service depends on and keep it from serving, using far more resource than the upload limit alone would permit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80189.json
- https://github.com/perber/leafwiki/releases/tag/v0.12.1
- https://github.com/perber/leafwiki/security/advisories/GHSA-258m-crqp-25xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-80189
- https://www.vulncheck.com/advisories/leafwiki-0.10.0-through-0.12.0-uncontrolled-resource-consumption-via-unbounded-zip-extraction
- https://github.com/perber/leafwiki
- https://github.com/perber/leafwiki/blob/v0.12.0/internal/importer/zip_extractor.go

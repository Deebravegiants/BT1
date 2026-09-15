# [M] phpUploader < 2.0.2 Unauthenticated Database Exposure via index model

## Summary
Severity: Medium
Advisory: CVE-2026-56124
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-56124
Type: osv

## Details
phpUploader before 2.0.2 contains an unauthenticated information disclosure vulnerability that allows remote attackers to access the full contents of the uploaded-files database table by visiting any page of the application. The index model executes an unbounded SELECT query and embeds the complete JSON-encoded result set in an inline script block, exposing uploader IP addresses, Argon2ID key hashes, internal filenames, and SHA-256 fingerprints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56124.json
- https://github.com/shimosyan/phpUploader/releases/tag/v2.0.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-56124
- https://www.vulncheck.com/advisories/phpuploader-unauthenticated-database-exposure-via-index-model
- https://github.com/shimosyan/phpUploader/pull/294
- https://github.com/shimosyan/phpUploader/commit/45dc4f1c9a2de5ade427deebad0148834c0e8c50
- https://github.com/shimosyan/phpUploader

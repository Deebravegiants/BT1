# [H] DataEase: Path Traversal Leading to Arbitrary File Deletion via Font Management

## Summary
Severity: High
Advisory: CVE-2026-55631
Aliases: GHSA-r99p-w8fc-93g6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-55631
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, the font management module allows authenticated users to submit an arbitrary fileTransName when creating a font record; when the record is later deleted, the backend concatenates that stored value with the font storage directory and passes it to FileUtils.deleteFile() without path traversal sanitization, allowing deletion of arbitrary writable files in the application container. This issue is fixed in version 2.10.24.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55631.json
- https://github.com/dataease/dataease/security/advisories/GHSA-r99p-w8fc-93g6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55631
- https://github.com/dataease/dataease/commit/8892a6945b0b7a329a156155270fae58afa895bc

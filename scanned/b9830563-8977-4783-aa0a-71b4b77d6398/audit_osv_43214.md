# [C] Budibase before 3.40.0 Arbitrary File Write via Path Traversal

## Summary
Severity: Critical
Advisory: CVE-2026-72850
Aliases: GHSA-pxwc-66g3-5f27
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72850
Type: osv

## Details
Budibase before 3.40.0 fails to properly sanitize S3 object keys, allowing authenticated builders to upload files with traversal sequences that are preserved during export. Attackers can craft filenames containing .. segments that escape the temporary directory during workspace export, writing arbitrary content to any path writable by the Budibase process.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-pxwc-66g3-5f27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72850.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72850
- https://www.vulncheck.com/advisories/budibase-before-arbitrary-file-write-via-path-traversal

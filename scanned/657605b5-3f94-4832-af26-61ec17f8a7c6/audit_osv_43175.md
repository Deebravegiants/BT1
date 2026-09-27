# [M] Grav before 2.0.16 Path Traversal via MediaUploadTrait deleteFile

## Summary
Severity: Medium
Advisory: CVE-2026-72695
Aliases: GHSA-jq29-c7v8-rg55
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-72695
Type: osv

## Details
Grav before 2.0.16 contains a path traversal vulnerability in MediaUploadTrait::deleteFile() that allows authenticated users with media management permissions to delete arbitrary files by supplying filenames with directory traversal sequences. The method validates only the basename portion of the filename while preserving unvalidated directory paths containing ../ sequences that are passed to unlink(), enabling deletion of files outside the intended media storage directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72695.json
- https://github.com/getgrav/grav/security/advisories/GHSA-jq29-c7v8-rg55
- https://nvd.nist.gov/vuln/detail/CVE-2026-72695
- https://www.vulncheck.com/advisories/grav-before-path-traversal-via-mediauploadtrait-deletefile

# [C] FileRise shared-folder upload path traversal allows arbitrary file write and admin takeover

## Summary
Severity: Critical
Advisory: CVE-2026-54414
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-54414
Type: osv

## Details
FileRise before 3.16.0 is vulnerable to path traversal in the shared-folder upload endpoint (/api/folder/uploadToSharedFolder.php), leading to arbitrary file write and administrator account takeover. The upload filename is validated by FolderController with basename and REGEX_FILE_NAME, which permit URL-encoded sequences (the regex blocks / and \ but not %).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54414
- https://github.com/error311/FileRise/releases/tag/v3.16.0
- https://github.com/error311/FileRise
- https://github.com/error311/FileRise/blob/v3.15.0/src/FileRise/Domain/UploadModel.php#L1023

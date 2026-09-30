# [C] Cockpit CMS Missing Authorization in Bucket File Storage API

## Summary
Severity: Critical
Advisory: CVE-2026-57855
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-57855
Type: osv

## Details
Cockpit CMS contains a missing authorization vulnerability in the Bucket file storage API (/system/buckets/api). The api() method in modules/System/Controller/Buckets.php executes bucket commands (ls, upload, removefiles, rename, createfolder) without performing any ACL or role check. Any authenticated user, regardless of role, can perform all bucket operations on any named bucket, including buckets intended for admin use only.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57855.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57855
- https://www.vulncheck.com/advisories/cockpit-cms-missing-authorization-in-bucket-file-storage-api
- https://github.com/Cockpit-HQ/Cockpit/commit/dde2d1d74f5f4e11de42a298918ea8c9684f932c
- https://github.com/cockpit-hq/cockpit
- https://gist.github.com/sermikr0/821c4edd3c34e98a62a50b07707785bd

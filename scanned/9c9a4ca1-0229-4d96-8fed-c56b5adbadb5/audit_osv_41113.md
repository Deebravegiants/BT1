# [C] Cockpit CMS Path Traversal via Bucket Name in Bucket File Storage API

## Summary
Severity: Critical
Advisory: CVE-2026-57856
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-57856
Type: osv

## Details
Cockpit CMS contains a path traversal vulnerability in the Bucket file storage API (/system/buckets/api). The api() method in modules/System/Controller/Buckets.php sanitizes the bucket name with preg_replace('/[^a-zA-Z0-9-_\\.]/','', $bucket), which permits '..' and '../' sequences. The sanitized value is interpolated into a Flysystem path as uploads://buckets/{bucket}. Flysystem's WhitespacePathNormalizer resolves 'buckets/..' to the empty string (the uploads storage root) without raising PathTraversalDetected because the '..' has a preceding component to consume. An authenticated low-privileged user can send a crafted request with a '../' bucket name to list, upload, and delete files across all buckets, including those belonging to other users or roles

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57856
- https://www.vulncheck.com/advisories/cockpit-cms-missing-authorization-in-bucket-file-storage-api
- https://www.vulncheck.com/advisories/cockpit-cms-path-traversal-via-bucket-name-in-bucket-file-storage-api
- https://github.com/Cockpit-HQ/Cockpit/commit/dde2d1d74f5f4e11de42a298918ea8c9684f932c
- https://github.com/cockpit-hq/cockpit
- https://gist.github.com/sermikr0/821c4edd3c34e98a62a50b07707785bd

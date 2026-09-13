# [M] ContiNew Admin through 4.1.0 Missing Authorization and File-Type Allowlist on Multipart Upload Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-80050
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80050
Type: osv

## Details
ContiNew Admin fails to apply file-upload permission checks or file-type allowlist validation to multipart upload endpoints, allowing authenticated users to store files with arbitrary extensions. Attackers can initialize chunked uploads, send file parts, and complete uploads to leave arbitrary files in the storage backend accessible via web server URLs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80050.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80050
- https://www.vulncheck.com/advisories/continew-admin-through-4.1.0-missing-authorization-and-file-type-allowlist-on-multipart-upload-endpoints
- https://github.com/continew-org/continew-admin/issues/221
- https://github.com/continew-org/continew-admin
- https://github.com/continew-org/continew-admin/blob/v4.1.0/continew-system/src/main/java/top/continew/admin/system/controller/MultipartUploadController.java

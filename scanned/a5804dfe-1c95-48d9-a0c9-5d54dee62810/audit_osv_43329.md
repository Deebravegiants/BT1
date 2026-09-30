# [M] RustFS: Version-specific object reads authorize the non-version action

## Summary
Severity: Medium
Advisory: CVE-2026-73265
Aliases: GHSA-3ppv-fx5m-m749
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73265
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. RustFS authorizes explicit versionId reads in GetObject, CopyObject sources, and UploadPartCopy sources with s3:GetObject instead of s3:GetObjectVersion, allowing principals without historical-version permission to disclose known historical object content. This issue is fixed in version 1.0.0-beta.11.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-beta.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73265.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-3ppv-fx5m-m749
- https://nvd.nist.gov/vuln/detail/CVE-2026-73265
- https://github.com/rustfs/rustfs/commit/81665617029e5e437ecf9dc70d8dcbbbf80cdbd1
- https://github.com/rustfs/rustfs/pull/5142

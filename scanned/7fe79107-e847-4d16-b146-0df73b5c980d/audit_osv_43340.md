# [M] RustFS: Anonymous ListObjectVersions bypasses RestrictPublicBuckets through the ListBucket fallback

## Summary
Severity: Medium
Advisory: CVE-2026-73290
Aliases: GHSA-x298-9x87-fvjq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73290
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.12, an anonymous ListObjectVersions request in rustfs/src/storage/access.rs that lacks a direct bucket-policy grant falls back to an s3:ListBucket check and returns before the policy_allowed path applies deny_anonymous_table_data_plane_if_needed and RestrictPublicBuckets, so a bucket that permits anonymous listing can continue exposing version listings after an operator enables the public-access control. The bypass affects GET /<bucket>?versions= and can disclose object version metadata even though equivalent GetObject requests are denied. This issue is fixed in version 1.0.0-beta.12.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-beta.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73290.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-x298-9x87-fvjq
- https://nvd.nist.gov/vuln/detail/CVE-2026-73290
- https://github.com/rustfs/rustfs/commit/92f83bfe155d8a3b9cdd903086e5b28d52339efb

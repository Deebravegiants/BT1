# [M] RustFS: FTPS MKD bypasses IAM CreateBucket authorization

## Summary
Severity: Medium
Advisory: CVE-2026-73287
Aliases: GHSA-g3vq-vv42-f647
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73287
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.12, RustFS handles FTPS MKD in FtpsDriver::mkd in crates/protocols/src/ftps/driver.rs by calling storage.create_bucket without authorize_operation for S3Action::CreateBucket, allowing authenticated FTPS users denied s3:CreateBucket to create buckets. This issue is fixed in version 1.0.0-beta.12.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-beta.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73287.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-g3vq-vv42-f647
- https://nvd.nist.gov/vuln/detail/CVE-2026-73287
- https://github.com/rustfs/rustfs/commit/92f83bfe155d8a3b9cdd903086e5b28d52339efb

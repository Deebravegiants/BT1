# [H] RustFS: ListRemoteTargetHandler authorization bypass leaks replication target credentials

## Summary
Severity: High
Advisory: CVE-2026-55188
Aliases: GHSA-796f-j7xp-hwf4
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-55188
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. From 1.0.0-alpha.1 until 1.0.0-beta.9, RustFS contains an authorization bypass in the bucket replication admin API. The ListRemoteTargetHandler handler for listing remote replication targets only checks whether request credentials exist, but does not verify that the caller has replication or administrator permissions. As a result, an authenticated user with no effective bucket or admin permissions can list remote replication target configuration for a bucket. Because the returned BucketTarget objects include remote target credentials, this can disclose replication access keys and secret keys. This vulnerability is fixed in 1.0.0-beta.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55188.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-796f-j7xp-hwf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55188

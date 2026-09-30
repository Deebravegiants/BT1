# [C] RustFS: Internode RPC HMAC secret falls back to public default credential, enabling peer impersonation

## Summary
Severity: Critical
Advisory: CVE-2026-45039
Aliases: GHSA-r5qv-rc46-hv8q
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45039
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.2, the internode RPC layer authenticates every request with an HMAC-SHA256 signature using a shared secret. The function that produces this secret, get_shared_secret() in crates/ecstore/src/rpc/http_auth.rs, falls back to the public, source-tree-embedded DEFAULT_SECRET_KEY = "rustfsadmin" when neither the RUSTFS_RPC_SECRET environment variable nor the global S3 secret key has been configured. This vulnerability is fixed in 1.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45039.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-r5qv-rc46-hv8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-45039

# [H] RustFS Snowball Auto-Extract: Path Traversal allows cross-bucket object injection

## Summary
Severity: High
Advisory: CVE-2026-49991
Aliases: GHSA-f4vq-9ffr-m8m3
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-49991
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. In 1.0.0-beta.4, authenticated users with only PutObject permission on their own bucket can exploit a path traversal vulnerability in the Snowball auto-extract feature to write arbitrary objects into other users' buckets, completely breaking multi-tenant isolation. The vulnerability chains three flaws: No ../ sanitization in tar entry key normalization; IAM wildcard matching uses raw (uncleaned) paths; and Filesystem path cleaning resolves ../ across bucket boundaries.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49991.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-f4vq-9ffr-m8m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-49991

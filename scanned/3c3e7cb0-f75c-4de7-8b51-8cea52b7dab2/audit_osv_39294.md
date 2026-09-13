# [M] RustFS: UploadPartCopy Does Not Enforce Destination Bucket Policy on Copy Source

## Summary
Severity: Medium
Advisory: CVE-2026-45042
Aliases: GHSA-wfxj-ph3v-7mjf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45042
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.2, improper authorization in the UploadPartCopy operation allows copying objects across buckets without enforcing destination bucket restrictions on allowed copy sources. The implementation validates GetObject permission on the source bucket and PutObject on the destination bucket independently, but does not enforce any policy constraints on whether the destination bucket permits the specified copy source. This enables unauthorized cross-bucket data movement. This vulnerability is fixed in 1.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45042.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-wfxj-ph3v-7mjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45042

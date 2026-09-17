# [M] Multiple Path Traversal Variants in awslabs/tough

## Summary
Severity: Medium
Advisory: CVE-2026-6968
Aliases: GHSA-v57p-gppj-p9vg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:L)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-6968
Type: osv

## Details
Incomplete path traversal fixes in awslabs/tough before tough-v0.22.0 allow remote authenticated users with delegated signing authority to write files outside intended output directories via absolute target names in copy_target/link_target, symlinked parent directories in save_target, or symlinked metadata filenames in SignedRole::write, because write paths trust the joined destination path without post-resolution containment verification.

We recommend you upgrade to tough-v0.22.0 / tuftool-v0.15.0.

## References
- https://aws.amazon.com/security/security-bulletins/2026-019-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6968.json
- https://github.com/awslabs/tough/security/advisories/GHSA-v57p-gppj-p9vg
- https://nvd.nist.gov/vuln/detail/CVE-2026-6968
- https://crates.io/crates/tough/0.22.0
- https://crates.io/crates/tuftool/0.15.0
- https://github.com/awslabs/tough/releases/tag/tough-v0.22.0
- https://github.com/awslabs/tough/releases/tag/tuftool-v0.15.0

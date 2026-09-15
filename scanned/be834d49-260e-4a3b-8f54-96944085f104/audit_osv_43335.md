# [H] RustFS: OPA policy plugin omits ExistingObjectTag conditions, allowing tag-based authorization policies to treat tagged objects as untagged

## Summary
Severity: High
Advisory: CVE-2026-73285
Aliases: GHSA-5w8r-p896-6vq2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73285
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. From 1.0.0-alpha.64 until 1.0.0-rc.1, RustFS external OPA authorization enabled by RUSTFS_POLICY_PLUGIN_URL in crates/iam/src/sys.rs sets PreparedIamAuth.needs_existing_object_tag incorrectly for PreparedIamMode::Opa, causing maybe_merge_object_tag_conditions to omit s3:ExistingObjectTag/* values and allowing authenticated users to bypass tag-based policy restrictions. This issue is fixed in version 1.0.0-rc.1.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-rc.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73285.json
- https://github.com/rustfs/rustfs/blob/380ed40b471887014fe21d069b61df9eacca074b/.agents/skills/security-advisory-lessons/references/advisory-patterns.md?plain=1#L47
- https://github.com/rustfs/rustfs/security/advisories/GHSA-5w8r-p896-6vq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73285
- https://github.com/rustfs/rustfs/commit/98d3619613722308498494d412797a52ea8ae64d

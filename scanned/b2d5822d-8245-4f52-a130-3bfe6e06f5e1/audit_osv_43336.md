# [H] RustF: Request headers can populate server-derived IAM condition keys, letting a caller satisfy identity-based policy conditions

## Summary
Severity: High
Advisory: CVE-2026-73286
Aliases: GHSA-6r96-hmgc-726c
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73286
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. Prior to 1.0.0-beta.12, RustFS get_condition_values folds attacker-controlled request headers from HeaderMap into server-derived userid, username, principaltype, groups, versionid, signatureversion, jwt:, and ldap: condition keys, allowing authenticated callers to satisfy identity-based policy conditions. This issue is fixed in version 1.0.0-beta.12.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-beta.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73286.json
- https://github.com/rustfs/rustfs/blob/380ed40b471887014fe21d069b61df9eacca074b/.agents/skills/security-advisory-lessons/references/advisory-patterns.md?plain=1#L45
- https://github.com/rustfs/rustfs/security/advisories/GHSA-6r96-hmgc-726c
- https://nvd.nist.gov/vuln/detail/CVE-2026-73286
- https://github.com/rustfs/rustfs/commit/92f83bfe155d8a3b9cdd903086e5b28d52339efb

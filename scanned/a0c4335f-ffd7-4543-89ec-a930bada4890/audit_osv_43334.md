# [H] RustFS: AddServiceAccount Handler Allows Creation of Root-Parent Service Accounts

## Summary
Severity: High
Advisory: CVE-2026-73284
Aliases: GHSA-5354-r3w2-34m8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73284
Type: osv

## Details
RustFS is a distributed object storage system built in Rust. RustFS AddServiceAccount in rustfs/src/admin/handlers/service_account.rs accepts an attacker-controlled target_user after only checking CreateServiceAccountAdminAction, passes it to new_service_account, and prepare_service_account_auth sets is_owner for the resulting root-parent service account. This issue is fixed in version 1.0.0-beta.11.

## References
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-beta.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73284.json
- https://github.com/rustfs/rustfs/security/advisories/GHSA-5354-r3w2-34m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-73284
- https://github.com/rustfs/rustfs/commit/9866f68d86482b3de7e0058a908727c3815e72b9
- https://github.com/rustfs/rustfs/pull/5141

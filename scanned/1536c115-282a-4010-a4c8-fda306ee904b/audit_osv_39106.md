# [H] Vaultwarden: Cross-Org Group Binding Enables Unauthorized Read And Write Access Into Another Organization

## Summary
Severity: High
Advisory: CVE-2026-43912
Aliases: GHSA-569v-845w-g82p
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43912
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.35.5, Vaultwarden does not enforce that a groups_users.users_organizations_uuid entry belongs to the same organization as groups.groups_uuid, or a collections_groups.collections_uuid entry belongs to the same organization as collections_groups.groups_uuid. Multiple organization group-management endpoints accept arbitrary MembershipId and CollectionId values and persist them directly without verifying org consistency. This lets an attacker who is Admin in Organization A, and only a low-privileged member in Organization B bind their Org B membership UUID into an Org A group, then use that foreign group relationship to gain unauthorized access to Org B vault data. With an accessAll=true Org A group, the attacker can make /api/sync and /api/ciphers enumerate Org B ciphers. Once those unauthorized sync results reveal Org B collection IDs, the attacker can also bind those foreign collection IDs to the Org A group and turn the same flaw into write access over Org B items. This vulnerability is fixed in 1.35.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43912.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-569v-845w-g82p
- https://nvd.nist.gov/vuln/detail/CVE-2026-43912

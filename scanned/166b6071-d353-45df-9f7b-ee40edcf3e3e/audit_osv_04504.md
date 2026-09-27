# [M] Discourse vulnerable to group membership addition permission bypass via discourse-policy plugin

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-28282
Aliases: CVE-2026-28282, GHSA-6cc8-x3rm-j5pf
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-28282
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.4.0

## Details
Discourse is an open-source discussion platform. Versions prior to 2026.3.0, 2026.2.1, and 2026.1.2 have a security flaw in the discourse-policy plugin which allowed a user with policy creation permission to gain membership access to any private/restricted groups. Once membership to a private/restricted group has been obtained, the user will be able to read private topics that only the group has access to. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. As a workaround, review all policies for the use of `add-users-to-group` and temporarily remove the attribute from the policy. Alternatively, disable the discourse-policy plugin by disabling the `policy_enabled` site setting.

## References
- https://github.com/discourse/discourse/commit/64e2514ac17046cfaa8bc68a3c5140bc40736add
- https://github.com/discourse/discourse/commit/c14b8a4cc5fc94e4839a83c5d55765897589f45b
- https://github.com/discourse/discourse/commit/dcde9de530f515e88f99957056ffbcc2e1e03951
- https://github.com/discourse/discourse/security/advisories/GHSA-6cc8-x3rm-j5pf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28282

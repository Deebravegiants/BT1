# [M] Potential bypass of chat permissions in Discourse

## Summary
Severity: Medium
Advisory: BIT-discourse-2024-53994
Aliases: CVE-2024-53994, GHSA-mrpw-gwj7-98r6
Ecosystem: Bitnami
Published: 2025-02-20
Source: https://osv.dev/vulnerability/BIT-discourse-2024-53994
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.3

## Details
Discourse is an open source platform for community discussion. In affected versions users who disable chat in preferences could still be reachable in some cases. This problem has been patched in the latest version of Discourse. Users are advised to upgrade. Users unable to upgrade should disable the chat plugin within site settings.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-mrpw-gwj7-98r6
- https://nvd.nist.gov/vuln/detail/CVE-2024-53994

# [M] Discourse may bypass user preference when adding users to chat groups

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-24972
Aliases: CVE-2025-24972, GHSA-4p63-qw6g-4mv2
Ecosystem: Bitnami
Published: 2025-03-28
Source: https://osv.dev/vulnerability/BIT-discourse-2025-24972
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.4.0

## Details
Discourse is an open-source discussion platform. Prior to versions `3.3.4` on the `stable` branch and `3.4.0.beta5` on the `beta` branch, in specific circumstances, users could be added to group direct messages despite disabling direct messaging in their preferences. Versions `3.3.4` and `3.4.0.beta5` contain a patch for the issue. A workaround is available. If a user disables chat in their preferences then they cannot be added to new group chats.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-4p63-qw6g-4mv2
- https://nvd.nist.gov/vuln/detail/CVE-2025-24972

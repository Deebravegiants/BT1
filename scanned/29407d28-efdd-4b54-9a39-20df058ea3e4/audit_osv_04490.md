# [M] Discourse has SQL injection in PM tag filtering

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27149
Aliases: CVE-2026-27149, GHSA-m6qf-h49w-h38w
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27149
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, SQL injection in PM tag filtering (`list_private_messages_tag`) allows bypassing tag filter conditions, potentially disclosing unauthorized private message metadata. Versions 2025.12.2, 2026.1.1, and 2026.2.0 patch the issue. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-m6qf-h49w-h38w
- https://nvd.nist.gov/vuln/detail/CVE-2026-27149

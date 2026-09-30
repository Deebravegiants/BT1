# [M] Discourse AI Discover's continue conversation allows threat actor to impersonate user

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-68660
Aliases: CVE-2025-68660, GHSA-mrvm-rprq-jqqh
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68660
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, an endpoint lets any authenticated user bypass the ai_discover_persona access controls and gain ongoing DM access to personas that may be wired to staff-only categories, RAG document sets, or automated tooling, enabling unauthorized data disclosure. Because the controller also accepts arbitrary user_id, an attacker can impersonate other accounts to trigger unwanted AI conversations on their behalf, generating confusing or abusive PM traffic. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-mrvm-rprq-jqqh
- https://nvd.nist.gov/vuln/detail/CVE-2025-68660

# [H] Discourse subscriptions are susceptible to takeover

## Summary
Severity: High
Advisory: BIT-discourse-2025-68479
Aliases: CVE-2025-68479, GHSA-6gjr-5897-m327
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68479
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, some subscription endpoints lack proper checking for ownership before making changes. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-6gjr-5897-m327
- https://nvd.nist.gov/vuln/detail/CVE-2025-68479

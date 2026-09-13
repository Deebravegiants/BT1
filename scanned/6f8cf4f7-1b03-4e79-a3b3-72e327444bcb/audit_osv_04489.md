# [M] Discourse: Poll voters endpoint lacked post visibility checks

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27021
Aliases: CVE-2026-27021, GHSA-f5m5-9hpw-7c2g
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27021
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, the voters endpoint in the poll plugin lacked post visibility checks which allowed unauthorized access to voters details of polls in any post. Versions 2025.12.2, 2026.1.1, and 2026.2.0 patch the issue. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-f5m5-9hpw-7c2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-27021

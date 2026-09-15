# [H] authentik: `UserSourceConnection.user` and `GroupSourceConnection.group` are changeable through the API

## Summary
Severity: High
Advisory: BIT-authentik-2026-49443
Aliases: CVE-2026-49443, GHSA-wr38-7xg8-fqxr
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-authentik-2026-49443
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.3.0 <2026.5.1

## Details
authentik is an open-source identity provider. Prior to versions 2025.12.6, 2026.2.4, and 2026.5.1, an attacker with the ability to change a source connection, and an account in one of the configured sources can log into any account. This issue has been patched in versions 2025.12.6, 2026.2.4, and 2026.5.1.

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-wr38-7xg8-fqxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-49443

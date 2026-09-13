# [C] authentik: SourceStage bypass via empty POST

## Summary
Severity: Critical
Advisory: BIT-authentik-2026-49448
Aliases: CVE-2026-49448, GHSA-xp7f-xjjx-gwm8
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-authentik-2026-49448
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.3.0 <2026.5.1

## Details
authentik is an open-source identity provider. Prior to versions 2025.12.6, 2026.2.4, and 2026.5.1, the Source stage can be bypassed by sending an empty POST. This issue has been patched in versions 2025.12.6, 2026.2.4, and 2026.5.1.

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-xp7f-xjjx-gwm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-49448

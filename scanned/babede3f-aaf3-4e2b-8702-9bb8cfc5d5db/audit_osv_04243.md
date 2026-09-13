# [H] authentik: SAML source does not validate Conditions, timing, or audience on assertions

## Summary
Severity: High
Advisory: BIT-authentik-2026-41577
Aliases: CVE-2026-41577, GHSA-4v4x-x5pr-8gp2
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-authentik-2026-41577
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.0.0 <2026.2.3

## Details
authentik is an open-source identity provider. Prior to versions 2025.12.5 and 2026.2.3, the SAML source response processor (ResponseProcessor.parse()) does not validate the Conditions element on assertions. NotBefore, NotOnOrAfter, and AudienceRestriction are all ignored. This allows replay of expired assertions and acceptance of assertions intended for other service providers. This issue has been patched in versions 2025.12.5 and 2026.2.3.

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-4v4x-x5pr-8gp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41577

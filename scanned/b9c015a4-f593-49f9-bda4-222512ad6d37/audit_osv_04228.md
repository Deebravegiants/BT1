# [C] Insufficient access control for OAuth2 Device Code flow in authentik

## Summary
Severity: Critical
Advisory: BIT-authentik-2024-38371
Aliases: CVE-2024-38371, GHSA-jq3m-37m7-gp45
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-38371
Type: osv

## Affected
- Bitnami: `authentik` — affected >=0 <2024.6.0

## Details
authentik is an open-source Identity Provider. Access restrictions assigned to an application were not checked when using the OAuth2 Device code flow. This could potentially allow users without the correct authorization to get OAuth tokens for an application and access it. This issue has been patched in version(s) 2024.6.0, 2024.2.4 and 2024.4.3.

## References
- https://github.com/goauthentik/authentik/releases/tag/version%2F2024.2.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2024.4.3
- https://github.com/goauthentik/authentik/releases/tag/version%2F2024.6.0
- https://github.com/goauthentik/authentik/security/advisories/GHSA-jq3m-37m7-gp45
- https://nvd.nist.gov/vuln/detail/CVE-2024-38371

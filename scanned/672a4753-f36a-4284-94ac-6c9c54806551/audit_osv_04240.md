# [H] authentik: Non-admin user can retrieve confidential OAuth client_secret via /api/v3/oauth2/access_tokens/

## Summary
Severity: High
Advisory: BIT-authentik-2026-40166
Aliases: CVE-2026-40166, GHSA-hhpc-rqgm-pxj4
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-authentik-2026-40166
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.2.0 <2026.2.3

## Details
authentik is an open-source identity provider. In versions prior to 2025.12.5 and 2026.2.0 through 2026.2.2, authenticated non-admin users with at least one OAuth2 access token can retrieve the client_secret of confidential OAuth2 providers they have previously authenticated against, exposing sensitive information to users without the correct permissions. This logic is GET /api/v3/oauth2/access_tokens/. The API response includes a nested provider object containing client_id and client_secret for providers configured with client_type: confidential, which should not be accessible to low-privilege users. This issue has been fixed in versions 2025.12.5 and 2026.2.3.

## References
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.12.5
- https://github.com/goauthentik/authentik/releases/tag/version%2F2026.2.3
- https://github.com/goauthentik/authentik/security/advisories/GHSA-hhpc-rqgm-pxj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40166

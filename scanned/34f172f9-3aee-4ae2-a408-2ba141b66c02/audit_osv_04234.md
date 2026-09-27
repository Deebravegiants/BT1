# [H] authentik's deletion of sessions did not revoke sessions when using database session storage

## Summary
Severity: High
Advisory: BIT-authentik-2025-29928
Aliases: CVE-2025-29928, GHSA-p6p8-f853-9g2p
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2025-29928
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2025.0.0 <2025.2.3

## Details
authentik is an open-source identity provider. Prior to versions 2024.12.4 and 2025.2.3, when authentik was configured to use the database for session storage (which is a non-default setting), deleting sessions via the Web Interface or the API would not revoke the session and the session holder would continue to have access to authentik. authentik 2025.2.3 and 2024.12.4 fix this issue. Switching to the cache-based session storage until the authentik instance can be upgraded is recommended. This will however also delete all existing sessions and users will have to re-authenticate.

## References
- https://github.com/goauthentik/authentik/commit/71294b7deb6eb5726a782de83b957eaf25fc4cf6
- https://github.com/goauthentik/authentik/security/advisories/GHSA-p6p8-f853-9g2p
- https://nvd.nist.gov/vuln/detail/CVE-2025-29928

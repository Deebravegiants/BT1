# [M] authentik: Unauthenticated LDAP directory data disclosure

## Summary
Severity: Medium
Advisory: BIT-authentik-2026-55106
Aliases: CVE-2026-55106, GHSA-h8ff-c3h7-2gf8
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-authentik-2026-55106
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.5.0 <2026.5.5

## Details
authentik is an open-source identity provider. Prior to 2026.2.6 and 2026.5.5, a diagnostic action on the LDAP Source API does not enforce the object-level read-authorization filter used by the rest of the API. Any party able to reach the API, including an unauthenticated client, can invoke the diagnostic action against a configured LDAP Source. The server then connects to the upstream directory using the source's configured bind credentials and returns a bounded set of directory entries. The response exposes the distinguished names of those entries and the names of the attributes present on them, revealing directory structure, naming conventions, and the existence of specific accounts and groups, but not attribute values. Deployments without a configured LDAP Source are not affected. This issue is fixed in versions 2026.2.6 and 2026.5.5.

## References
- https://github.com/goauthentik/authentik/commit/e638de23217480854ec5e48ca6fceae479321f99
- https://github.com/goauthentik/authentik/commit/fc336da4bd32bef52800c77d91aa0b82c5533041
- https://github.com/goauthentik/authentik/pull/24055
- https://github.com/goauthentik/authentik/pull/24060
- https://github.com/goauthentik/authentik/releases/tag/version/2026.2.6
- https://github.com/goauthentik/authentik/releases/tag/version/2026.5.5
- https://github.com/goauthentik/authentik/security/advisories/GHSA-h8ff-c3h7-2gf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-55106

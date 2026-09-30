# [C] authentik affected by Remote Code Execution via Context Key Injection in PropertyMapping Test Endpoint

## Summary
Severity: Critical
Advisory: BIT-authentik-2026-25227
Aliases: CVE-2026-25227, GHSA-qvxx-mfm6-626f
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2026-25227
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2025.10.0 <2025.12.4

## Details
authentik is an open-source identity provider. From 2021.3.1 to before 2025.8.6, 2025.10.4, and 2025.12.4, when using delegated permissions, a User that has the permission Can view * Property Mapping or Can view Expression Policy is able to execute arbitrary code within the authentik server container through the test endpoint, which is intended to preview how a property mapping/policy works. authentik 2025.8.6, 2025.10.4, and 2025.12.4 fix this issue.

## References
- https://github.com/goauthentik/authentik/commit/c691afaef164cf73c10a26a944ef2f11dbb1ac80
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.10.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.12.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.8.6
- https://github.com/goauthentik/authentik/security/advisories/GHSA-qvxx-mfm6-626f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25227

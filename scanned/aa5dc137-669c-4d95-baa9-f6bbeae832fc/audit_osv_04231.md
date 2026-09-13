# [H] authentik performs insufficient validation of OAuth scopes

## Summary
Severity: High
Advisory: BIT-authentik-2024-52287
Aliases: CVE-2024-52287, GHSA-v6m7-8j37-8f4v
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-52287
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2024.10.0 <2024.10.3

## Details
authentik is an open-source identity provider. When using the client_credentials or device_code OAuth grants, it was possible for an attacker to get a token from authentik with scopes that haven't been configured in authentik. authentik 2024.8.5 and 2024.10.3 fix this issue.

## References
- https://github.com/goauthentik/authentik/commit/e9c29e1644e9199b4ba58d2b10eb8c322138eea2
- https://github.com/goauthentik/authentik/security/advisories/GHSA-v6m7-8j37-8f4v
- https://nvd.nist.gov/vuln/detail/CVE-2024-52287

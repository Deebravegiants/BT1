# [C] OAuth2: PKCE can be fully circumvented

## Summary
Severity: Critical
Advisory: BIT-authentik-2023-48228
Aliases: CVE-2023-48228, GHSA-fm34-v8xq-f2c3
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2023-48228
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2023.10.0 <2023.10.4

## Details
authentik is an open-source identity provider. When initialising a oauth2 flow with a `code_challenge` and `code_method` (thus requesting PKCE), the single sign-on provider (authentik) must check if there is a matching and existing `code_verifier` during the token step. Prior to versions 2023.10.4 and 2023.8.5, authentik checks if the contents of `code_verifier` is matching only when it is provided. When it is left out completely, authentik simply accepts the token request with out it; even when the flow was started with a `code_challenge`. authentik 2023.8.5 and 2023.10.4 fix this issue.

## References
- https://github.com/goauthentik/authentik/blob/dd4e9030b4e667d3720be2feda24c08972602274/authentik/providers/oauth2/views/token.py#L225
- https://github.com/goauthentik/authentik/commit/3af77ab3821fe9c7df8055ba5eade3d1ecea03a6
- https://github.com/goauthentik/authentik/commit/6b9afed21f7c39f171a4a445654cfe415bba37d5
- https://github.com/goauthentik/authentik/commit/b88e39411c12e3f9e04125a7887f12354f760a14
- https://github.com/goauthentik/authentik/pull/7666
- https://github.com/goauthentik/authentik/pull/7668
- https://github.com/goauthentik/authentik/pull/7669
- https://github.com/goauthentik/authentik/releases/tag/version%2F2023.10.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2023.8.5
- https://github.com/goauthentik/authentik/security/advisories/GHSA-fm34-v8xq-f2c3
- https://nvd.nist.gov/vuln/detail/CVE-2023-48228

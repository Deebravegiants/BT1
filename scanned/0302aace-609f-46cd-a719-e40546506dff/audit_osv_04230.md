# [M] authentik cross-provider token validation problems

## Summary
Severity: Medium
Advisory: BIT-authentik-2024-47077
Aliases: CVE-2024-47077, GHSA-8gfm-pr6x-pfh9
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-47077
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2024.8.0 <2024.8.3

## Details
authentik is an open-source identity provider. Prior to versions 2024.8.3 and 2024.6.5, access tokens issued to one application can be stolen by that application and used to impersonate the user against any other proxy provider. Also, a user can steal an access token they were legitimately issued for one application and use it to access another application that they aren't allowed to access. Anyone who has more than one proxy provider application with different trust domains or different access control is affected. Versions 2024.8.3 and 2024.6.5 fix the issue.

## References
- https://github.com/goauthentik/authentik/blob/70b5a214f2e7205572f914aaf68682501b9f5945/authentik/providers/oauth2/views/introspection.py#L42-L51
- https://github.com/goauthentik/authentik/blob/70b5a214f2e7205572f914aaf68682501b9f5945/internal/outpost/proxyv2/application/auth_bearer.go#L30-L36
- https://github.com/goauthentik/authentik/commit/22e586bd8cdc3d1db8a0f18314d76f82371129b2
- https://github.com/goauthentik/authentik/commit/57a31b5dd16d4adce716b9878455c0d6f58155fe
- https://github.com/goauthentik/authentik/security/advisories/GHSA-8gfm-pr6x-pfh9
- https://nvd.nist.gov/vuln/detail/CVE-2024-47077

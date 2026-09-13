# [H] Improper Access Control and Incorrect Authorization in github.com/goauthentik/authentik

## Summary
Severity: High
Advisory: BIT-authentik-2024-37905
Aliases: CVE-2024-37905, GHSA-c78c-2r9w-p7x4
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-37905
Type: osv

## Affected
- Bitnami: `authentik` — affected >=0 <2024.6.0

## Details
authentik is an open-source Identity Provider that emphasizes flexibility and versatility. Authentik API-Access-Token mechanism can be exploited to gain admin user privileges. A successful exploit of the issue will result in a user gaining full admin access to the Authentik application, including resetting user passwords and more. This issue has been patched in version(s) 2024.2.4, 2024.4.2 and 2024.6.0.

## References
- https://github.com/goauthentik/authentik/releases/tag/version%2F2024.2.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2024.4.3
- https://github.com/goauthentik/authentik/releases/tag/version%2F2024.6.0
- https://github.com/goauthentik/authentik/security/advisories/GHSA-c78c-2r9w-p7x4
- https://nvd.nist.gov/vuln/detail/CVE-2024-37905

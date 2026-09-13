# [C] authentik has an insecure default configuration for OAuth2 Redirect URIs

## Summary
Severity: Critical
Advisory: BIT-authentik-2024-52289
Aliases: CVE-2024-52289, GHSA-3q5w-6m3x-64gj
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2024-52289
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2024.10.0 <2024.10.3

## Details
authentik is an open-source identity provider. Redirect URIs in the OAuth2 provider in authentik are checked by RegEx comparison.
When no Redirect URIs are configured in a provider, authentik will automatically use the first redirect_uri value received as an allowed redirect URI, without escaping characters that have a special meaning in RegEx. Similarly, the documentation did not take this into consideration either. Given a provider with the Redirect URIs set to https://foo.example.com, an attacker can register a domain fooaexample.com, and it will correctly pass validation. authentik 2024.8.5 and 2024.10.3 fix this issue. As a workaround, When configuring OAuth2 providers, make sure to escape any wildcard characters that are not intended to function as a wildcard, for example replace `.` with `\.`.

## References
- https://github.com/goauthentik/authentik/commit/85bb638243c8d7ea42ddd3b15b3f51a90d2b8c54
- https://github.com/goauthentik/authentik/security/advisories/GHSA-3q5w-6m3x-64gj
- https://nvd.nist.gov/vuln/detail/CVE-2024-52289
- https://www.vicarius.io/vsociety/posts/cve-2024-52289-detect-authentik-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2024-52289-mitigate-authentik-vulnerability

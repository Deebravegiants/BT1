# [M] Subdomain checking of whitelisted domains could allow unintended redirects

## Summary
Severity: Medium
Advisory: BIT-oauth2-proxy-2021-21291
Aliases: CVE-2021-21291, GHSA-4mf2-f3wh-gvf2, GO-2022-0790
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-oauth2-proxy-2021-21291
Type: osv

## Affected
- Bitnami: `oauth2-proxy` — affected >=0 <7.0.0

## Details
OAuth2 Proxy is an open-source reverse proxy and static file server that provides authentication using Providers (Google, GitHub, and others) to validate accounts by email, domain or group. In OAuth2 Proxy before version 7.0.0, for users that use the whitelist domain feature, a domain that ended in a similar way to the intended domain could have been allowed as a redirect. For example, if a whitelist domain was configured for ".example.com", the intention is that subdomains of example.com are allowed. Instead, "example.com" and "badexample.com" could also match. This is fixed in version 7.0.0 onwards. As a workaround, one can disable the whitelist domain feature and run separate OAuth2 Proxy instances for each subdomain.

## References
- https://github.com/oauth2-proxy/oauth2-proxy/commit/780ae4f3c99b579cb2ea9845121caebb6192f725
- https://github.com/oauth2-proxy/oauth2-proxy/releases/tag/v7.0.0
- https://github.com/oauth2-proxy/oauth2-proxy/security/advisories/GHSA-4mf2-f3wh-gvf2
- https://pkg.go.dev/github.com/oauth2-proxy/oauth2-proxy/v7
- https://nvd.nist.gov/vuln/detail/CVE-2021-21291

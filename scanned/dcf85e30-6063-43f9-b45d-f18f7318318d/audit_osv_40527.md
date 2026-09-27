# [H] Boruta accepts expired JWT client assertions due to missing exp claim validation

## Summary
Severity: High
Advisory: CVE-2026-53431
Aliases: EEF-CVE-2026-53431, GHSA-xjv8-vmh5-xhf6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-53431
Type: osv

## Details
Authentication Bypass by Capture-replay vulnerability in malach-it Boruta allows an attacker who has obtained a previously valid JWT client assertion to authenticate as the issuing OAuth client after the assertion has expired.

Boruta accepts JWT-based client authentication (client_secret_jwt and private_key_jwt token endpoint authentication methods) but never enforces that the assertion's exp claim is in the future. The pre-check helper Boruta.Oauth.Request.Base.check_expiration/1 in lib/boruta/oauth/request/base.ex only verifies that an exp claim is present (it pattern-matches on the existence of the key and returns success), and the Joken token configuration used for signature verification, Boruta.Oauth.Authorization.Client.Token.token_config/0 in lib/boruta/oauth/authorization/client.ex, returns an empty map, so Joken's default exp claim validator is not engaged either. Any attacker who obtains a validly-signed client assertion (for example through logs, reverse proxies, browser tooling, or other observability surfaces) can replay it indefinitely to authenticate as the client and obtain access tokens with that client's privileges.

This issue affects boruta: from 2.3.0 before 2.3.7.

## References
- https://cna.erlef.org/cves/CVE-2026-53431.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-53431
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53431.json
- https://github.com/malach-it/boruta_auth/security/advisories/GHSA-xjv8-vmh5-xhf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-53431
- https://github.com/malach-it/boruta_auth/commit/5204f88f9b2cdd9637a755337ed5f99185be5474
- https://github.com/malach-it/boruta_auth/commit/69363432aa36760fc5438e4e17115d0f7c1b925a
- https://github.com/malach-it/boruta_auth

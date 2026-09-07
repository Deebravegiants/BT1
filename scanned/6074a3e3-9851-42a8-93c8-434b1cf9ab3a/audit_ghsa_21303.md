# [C] Caddy vulnerable to Authentication Bypass due to mishandling of TLS client authentication

## Summary
Severity: Critical
Advisory: GHSA-gr7w-x2jp-3xgw
CVE: CVE-2018-21246
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-gr7w-x2jp-3xgw
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy` — affected >=0 <0.10.13

## Details
Caddy before 0.10.13 mishandles TLS client authentication, as demonstrated by an authentication bypass caused by the lack of the StrictHostMatching mode.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21246
- https://github.com/caddyserver/caddy/pull/2099
- https://github.com/caddyserver/caddy/commit/4d9ee000c8d2cbcdd8284007c1e0f2da7bc3c7c3
- https://bugs.gentoo.org/715214
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v0.10.13
- https://pkg.go.dev/vuln/GO-2020-0043

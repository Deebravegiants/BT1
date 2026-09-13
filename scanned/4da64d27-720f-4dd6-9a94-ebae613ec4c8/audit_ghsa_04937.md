# [H] undici vulnerable to cross-origin request routing via SOCKS5 proxy pool reuse

## Summary
Severity: High
Advisory: GHSA-hm92-r4w5-c3mj
CVE: CVE-2026-6734
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-hm92-r4w5-c3mj
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.23.0 <7.28.0
- npm: `undici` — affected >=8.0.0 <8.2.0

## Details
## Impact

When using `Socks5ProxyAgent`, undici reuses a single connection pool across different origins without verifying that the pool's origin matches the requested origin. All requests are dispatched through the pool connected to the first origin, regardless of the intended destination.

This causes cross-origin request routing: credentials and request data intended for origin B are sent to origin A, responses from the wrong origin are trusted, and HTTPS requests may be silently downgraded to HTTP.

Impacted users are applications that use `Socks5ProxyAgent` (directly or via `setGlobalDispatcher`) and make requests to more than one origin.

This was introduced in undici 7.23.0 via [#4385](https://github.com/nodejs/undici/pull/4385) and affects all versions through 8.1.0.

## Patches

Upgrade to undici v7.28.0 or v8.2.0

## Workarounds

Use a separate `Socks5ProxyAgent` instance per origin, or avoid using `Socks5ProxyAgent` with multiple origins.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-hm92-r4w5-c3mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-6734
- https://github.com/nodejs/undici/pull/5041
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici

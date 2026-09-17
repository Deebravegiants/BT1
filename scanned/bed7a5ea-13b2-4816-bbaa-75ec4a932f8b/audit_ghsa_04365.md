# [H] undici vulnerable to TLS certificate validation bypass via dropped requestTls in SOCKS5 ProxyAgent

## Summary
Severity: High
Advisory: GHSA-vmh5-mc38-953g
CVE: CVE-2026-9697
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-vmh5-mc38-953g
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.23.0 <7.28.0
- npm: `undici` — affected >=8.0.0 <8.5.0

## Details
## Impact

undici's `ProxyAgent` silently drops the `requestTls` option when configured with a SOCKS5 proxy URI (`socks5://` or `socks://`). The target HTTPS connection through the SOCKS5 tunnel falls back to Node's default trust store, ignoring user-configured `ca`, `cert`, `key`, `rejectUnauthorized`, and `servername` settings.

Applications that pin to an internal or corporate CA via `requestTls.ca` will, when their proxy URI is SOCKS5, get the default Mozilla CA bundle as the trust anchor instead. Any cert signed by any publicly-trusted CA for the target hostname is accepted, breaking the intended pin and enabling MITM read and tamper of the HTTPS exchange.

Affected applications are those that use undici's `ProxyAgent` (or `Socks5ProxyAgent` directly) with SOCKS5 AND rely on `requestTls` for TLS scope restriction. The bug was introduced in undici 7.23.0 when SOCKS5 support was added.

## Patches

Upgrade to undici v7.28.0 or v8.5.0.

## Workarounds

No workaround is available within the SOCKS5 path. If a SOCKS5 proxy with TLS scope restriction is required and an upgrade is not yet possible, route the traffic through an HTTP-proxy `ProxyAgent` instead, where `requestTls` is honored correctly.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-vmh5-mc38-953g
- https://nvd.nist.gov/vuln/detail/CVE-2026-9697
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici

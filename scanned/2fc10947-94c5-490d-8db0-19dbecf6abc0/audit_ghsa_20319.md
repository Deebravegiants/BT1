# [H] ProxyAgent vulnerable to MITM

## Summary
Severity: High
Advisory: GHSA-pgw7-wx7w-2w33
CVE: CVE-2022-32210
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-pgw7-wx7w-2w33
Type: github-advisory

## Affected
- npm: `undici` — affected >=4.8.2 <5.5.1

## Details
### Description

`Undici.ProxyAgent` never verifies the remote server's certificate, and always exposes all request & response data to the proxy. This unexpectedly means that proxies can MitM all HTTPS traffic, and if the proxy's URL is HTTP then it also means that nominally HTTPS requests are actually sent via plain-text HTTP between Undici and the proxy server.

### Impact

This affects all use of HTTPS via HTTP proxy using **`Undici.ProxyAgent`**  with Undici or Node's global `fetch`. In this case, it removes all HTTPS security from all requests sent using Undici's `ProxyAgent`, allowing trivial MitM attacks by anybody on the network path between the client and the target server (local network users, your ISP, the proxy, the target server's ISP, etc).
This less seriously affects HTTPS via HTTPS proxies. When you send HTTPS via a proxy to a remote server, the proxy can freely view or modify all HTTPS traffic unexpectedly (but only the proxy). 

### Patches

This issue was patched in Undici v5.5.1.

### Workarounds

At the time of writing, the only workaround is to not use `ProxyAgent` as a dispatcher for TLS Connections.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-pgw7-wx7w-2w33
- https://nvd.nist.gov/vuln/detail/CVE-2022-32210
- https://hackerone.com/reports/1583680
- https://github.com/nodejs/undici

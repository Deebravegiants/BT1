# [C] ALPINE-CVE-2026-8927

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-8927
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8927
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.12.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.12.0 <8.21.0-r0

## Details
When reusing a libcurl handle for sequential transfers driven by
environment-variable proxy configuration, libcurl fails to clear the proxy
authentication state between requests. Specifically, if the initial transfer
authenticates against `proxyA` using Digest auth, a subsequent transfer routed
through `proxyB` erroneously leaks the `Proxy-Authorization:` header intended
solely for `proxyA`.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8927

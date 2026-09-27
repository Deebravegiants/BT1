# [M] ALPINE-CVE-2026-7168

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-7168
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-7168
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.12.0 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.12.0 <8.20.0-r0

## Details
Successfully using libcurl to do a transfer over a specific HTTP proxy
(`proxyA`) with **Digest** authentication and then changing the proxy host to
a second one (`proxyB`) for a second transfer, reusing the same handle, makes
libcurl wrongly pass on the `Proxy-Authorization:` header field meant for
`proxyA`, to `proxyB`.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-7168

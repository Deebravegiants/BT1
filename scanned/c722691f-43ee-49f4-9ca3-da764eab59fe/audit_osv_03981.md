# [H] ALPINE-CVE-2026-8932

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-8932
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8932
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.7 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.7 <8.21.0-r0

## Details
libcurl would reuse a previously created connection even when some mTLS config
related option had been changed that should have prohibited reuse.

libcurl keeps previously used connections in a connection pool for subsequent
transfers to reuse if one of them matches the setup. However, some TLS
settings related to client certificates were left out from the configuration
match checks, making them match too easily. In particular options related to
the private key.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8932

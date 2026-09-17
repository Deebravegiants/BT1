# [H] ALPINE-CVE-2026-82208

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-82208
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-82208
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
With the wolfSSL backend, when CA caching is enabled and an
`CURLOPT_SSL_CTX_FUNCTION` callback replaces the trust store, libcurl can
silently reinstall the cached store after the callback returns. A certificate
trusted by the cached store but rejected by the callback-selected store is
then incorrectly accepted.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-82208

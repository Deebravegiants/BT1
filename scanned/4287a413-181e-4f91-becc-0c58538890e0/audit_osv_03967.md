# [H] ALPINE-CVE-2026-80230

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-80230
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-80230
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
When `CURLOPT_PINNEDPUBLICKEY` is configured alongside options that disable
standard peer verification (`CURLOPT_SSL_VERIFYPEER = 0` and
`CURLOPT_SSL_VERIFYHOST = 0`), libcurl fails to enforce public key pinning on
connections established without a presented server certificate. Bypassing the
pinning check under these disabled-verification conditions allows
unauthenticated connections to succeed when they should be rejected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-80230

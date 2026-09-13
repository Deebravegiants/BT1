# [H] ALPINE-CVE-2026-6276

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-6276
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-6276
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.71.0 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=7.71.0 <8.20.0-r0

## Details
Using libcurl, when a custom `Host:` header is first set for an HTTP request
and a second request is subsequently done using the same *easy handle* but
without the custom `Host:` header set, the second request would use stale
information and pass on cookies meant for the first host in the second
request. Leak them.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-6276

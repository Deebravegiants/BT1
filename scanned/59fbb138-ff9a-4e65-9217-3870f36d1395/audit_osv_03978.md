# [C] ALPINE-CVE-2026-8925

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-8925
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8925
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.15.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.15.0 <8.21.0-r0

## Details
The curl logic that works with SASL authentication could end up cleaning up
the GSASL context *twice* without clearing the pointer in between, making it
`free()` the same pointer twice.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8925

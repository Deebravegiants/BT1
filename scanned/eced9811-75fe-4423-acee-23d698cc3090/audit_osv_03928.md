# [M] ALPINE-CVE-2026-7009

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-7009
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-7009
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.17.0 <8.20.0-r0
- Alpine:v3.24: `curl` — affected >=8.17.0 <8.20.0-r0

## Details
When curl is told to use the Certificate Status Request TLS extension, often
referred to as *OCSP stapling*, to verify that the server certificate is
valid, it fails to detect OCSP problems and instead wrongly consider the
response as fine.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-7009

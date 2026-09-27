# [M] ALPINE-CVE-2023-46219

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46219
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46219
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.16: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.17: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.18: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.19: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.20: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.21: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.22: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.23: `curl` — affected >=7.84.0 <8.5.0-r0
- Alpine:v3.24: `curl` — affected >=7.84.0 <8.5.0-r0

## Details
When saving HSTS data to an excessively long file name, curl could end up
removing all contents, making subsequent requests using that file unaware of
the HSTS status they should otherwise use.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46219

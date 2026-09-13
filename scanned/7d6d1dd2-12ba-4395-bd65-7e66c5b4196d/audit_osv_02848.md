# [H] ALPINE-CVE-2023-36664

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-36664
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-36664
Type: osv

## Affected
- Alpine:v3.15: `ghostscript` — affected >=0 <9.55.0-r2
- Alpine:v3.16: `ghostscript` — affected >=0 <9.56.1-r2

## Details
Artifex Ghostscript before 10.01.2 mishandles permission validation for pipe devices (with the %pipe% prefix or the | pipe character prefix).

## References
- https://security.alpinelinux.org/vuln/CVE-2023-36664

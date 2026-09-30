# [H] ALPINE-CVE-2022-44617

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-44617
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-44617
Type: osv

## Affected
- Alpine:v3.14: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.15: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.16: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.17: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.18: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.19: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.20: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.21: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.22: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.23: `libxpm` — affected >=0 <3.5.15-r0
- Alpine:v3.24: `libxpm` — affected >=0 <3.5.15-r0

## Details
A flaw was found in libXpm. When processing a file with width of 0 and a very large height, some parser functions will be called repeatedly and can lead to an infinite loop, resulting in a Denial of Service in the application linked to the library.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-44617

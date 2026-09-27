# [H] ALPINE-CVE-2022-4883

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-4883
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4883
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
A flaw was found in libXpm. When processing files with .Z or .gz extensions, the library calls external programs to compress and uncompress files, relying on the PATH environment variable to find these programs, which could allow a malicious user to execute other programs by manipulating the PATH environment variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4883

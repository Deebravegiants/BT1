# [H] ALPINE-CVE-2025-0840

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-0840
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-0840
Type: osv

## Affected
- Alpine:v3.18: `binutils` — affected >=0 <2.40-r8
- Alpine:v3.19: `binutils` — affected >=0 <2.41-r1
- Alpine:v3.20: `binutils` — affected >=0 <2.42-r1
- Alpine:v3.21: `binutils` — affected >=0 <2.43.1-r2
- Alpine:v3.22: `binutils` — affected >=0 <2.44-r0
- Alpine:v3.23: `binutils` — affected >=0 <2.44-r0
- Alpine:v3.24: `binutils` — affected >=0 <2.44-r0

## Details
A vulnerability, which was classified as problematic, was found in GNU Binutils up to 2.43. This affects the function disassemble_bytes of the file binutils/objdump.c. The manipulation of the argument buf leads to stack-based buffer overflow. It is possible to initiate the attack remotely. The complexity of an attack is rather high. The exploitability is told to be difficult. The exploit has been disclosed to the public and may be used. Upgrading to version 2.44 is able to address this issue. The identifier of the patch is baac6c221e9d69335bf41366a1c7d87d8ab2f893. It is recommended to upgrade the affected component.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-0840

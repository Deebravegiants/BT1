# [H] ALPINE-CVE-2021-33560

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-33560
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-33560
Type: osv

## Affected
- Alpine:v3.11: `libgcrypt` — affected >=1.9.0 <1.8.8-r0
- Alpine:v3.12: `libgcrypt` — affected >=1.9.0 <1.8.8-r0
- Alpine:v3.13: `libgcrypt` — affected >=1.9.0 <1.8.8-r0
- Alpine:v3.14: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.15: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.16: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.17: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.18: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.19: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.20: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.21: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.22: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.23: `libgcrypt` — affected >=1.9.0 <1.9.4-r0
- Alpine:v3.24: `libgcrypt` — affected >=1.9.0 <1.9.4-r0

## Details
Libgcrypt before 1.8.8 and 1.9.x before 1.9.3 mishandles ElGamal encryption because it lacks exponent blinding to address a side-channel attack against mpi_powm, and the window size is not chosen appropriately. This, for example, affects use of ElGamal in OpenPGP.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-33560

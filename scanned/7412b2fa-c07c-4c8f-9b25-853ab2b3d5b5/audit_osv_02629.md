# [M] ALPINE-CVE-2022-38533

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-38533
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-38533
Type: osv

## Affected
- Alpine:v3.17: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.18: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.19: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.20: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.21: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.22: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.23: `binutils` — affected >=0 <2.39-r2
- Alpine:v3.24: `binutils` — affected >=0 <2.39-r2

## Details
In GNU Binutils before 2.40, there is a heap-buffer-overflow in the error function bfd_getl32 when called from the strip_main function in strip-new via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-38533

# [H] ALPINE-CVE-2021-43618

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-43618
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-43618
Type: osv

## Affected
- Alpine:v3.12: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.13: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.14: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.15: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.16: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.17: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.18: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.19: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.20: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.21: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.22: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.23: `gmp` — affected >=0 <6.2.1-r1
- Alpine:v3.24: `gmp` — affected >=0 <6.2.1-r1

## Details
GNU Multiple Precision Arithmetic Library (GMP) through 6.2.1 has an mpz/inp_raw.c integer overflow and resultant buffer overflow via crafted input, leading to a segmentation fault on 32-bit platforms.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-43618

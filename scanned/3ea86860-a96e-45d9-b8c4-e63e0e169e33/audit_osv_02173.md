# [H] ALPINE-CVE-2021-28706

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28706
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28706
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=3.2 <4.13.4-r2
- Alpine:v3.12: `xen` — affected >=3.2 <4.13.4-r3
- Alpine:v3.13: `xen` — affected >=3.2 <4.14.5-r0
- Alpine:v3.14: `xen` — affected >=3.2 <4.15.2-r0
- Alpine:v3.15: `xen` — affected >=3.2 <4.15.2-r0

## Details
guests may exceed their designated memory limit When a guest is permitted to have close to 16TiB of memory, it may be able to issue hypercalls to increase its memory allocation beyond the administrator established limit. This is a result of a calculation done with 32-bit precision, which may overflow. It would then only be the overflowed (and hence small) number which gets compared against the established upper bound.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28706

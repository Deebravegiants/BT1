# [M] ALPINE-CVE-2018-14679

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14679
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14679
Type: osv

## Affected
- Alpine:v3.10: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.11: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.5: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.6: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.7: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.8: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.9: `libmspack` — affected >=0 <0.7.1_alpha-r0

## Details
An issue was discovered in mspack/chmd.c in libmspack before 0.7alpha. There is an off-by-one error in the CHM PMGI/PMGL chunk number validity checks, which could lead to denial of service (uninitialized data dereference and application crash).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14679

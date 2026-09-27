# [M] ALPINE-CVE-2018-18584

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-18584
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18584
Type: osv

## Affected
- Alpine:v3.10: `cabextract` — affected >=0 <1.8-r0
- Alpine:v3.11: `cabextract` — affected >=0 <1.8-r0
- Alpine:v3.6: `cabextract` — affected >=0 <1.8-r0
- Alpine:v3.7: `cabextract` — affected >=0 <1.8-r0
- Alpine:v3.8: `cabextract` — affected >=0 <1.8-r0
- Alpine:v3.9: `cabextract` — affected >=0 <1.8-r0
- Alpine:v3.10: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.11: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.6: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.7: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.8: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.9: `libmspack` — affected >=0 <0.8_alpha-r0

## Details
In mspack/cab.h in libmspack before 0.8alpha and cabextract before 1.8, the CAB block input buffer is one byte too small for the maximal Quantum block, leading to an out-of-bounds write.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18584

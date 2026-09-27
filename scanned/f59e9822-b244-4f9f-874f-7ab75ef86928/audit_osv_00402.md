# [M] ALPINE-CVE-2017-11423

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-11423
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11423
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.99.4-r0
- Alpine:v3.10: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.11: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.3: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.4: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.5: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.6: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.7: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.8: `libmspack` — affected >=0 <0.5_alpha-r1
- Alpine:v3.9: `libmspack` — affected >=0 <0.5_alpha-r1

## Details
The cabd_read_string function in mspack/cabd.c in libmspack 0.5alpha, as used in ClamAV 0.99.2 and other products, allows remote attackers to cause a denial of service (stack-based buffer over-read and application crash) via a crafted CAB file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11423

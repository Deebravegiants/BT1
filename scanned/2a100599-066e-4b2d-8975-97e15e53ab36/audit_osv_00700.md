# [H] ALPINE-CVE-2017-6419

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6419
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6419
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
mspack/lzxd.c in libmspack 0.5alpha, as used in ClamAV 0.99.2, allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted CHM file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6419

# [H] ALPINE-CVE-2018-14681

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14681
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14681
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.100.2-r0
- Alpine:v3.10: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.11: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.5: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.6: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.7: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.8: `libmspack` — affected >=0 <0.7.1_alpha-r0
- Alpine:v3.9: `libmspack` — affected >=0 <0.7.1_alpha-r0

## Details
An issue was discovered in kwajd_read_headers in mspack/kwajd.c in libmspack before 0.7alpha. Bad KWAJ file header extensions could cause a one or two byte overwrite.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14681

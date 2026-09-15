# [M] ALPINE-CVE-2018-18585

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-18585
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18585
Type: osv

## Affected
- Alpine:v3.10: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.11: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.6: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.7: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.8: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.9: `libmspack` — affected >=0 <0.8_alpha-r0

## Details
chmd_read_headers in mspack/chmd.c in libmspack before 0.8alpha accepts a filename that has '\0' as its first or second character (such as the "/\0" name).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18585

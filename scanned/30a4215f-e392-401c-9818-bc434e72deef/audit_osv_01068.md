# [M] ALPINE-CVE-2018-18586

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-18586
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18586
Type: osv

## Affected
- Alpine:v3.10: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.11: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.6: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.7: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.8: `libmspack` — affected >=0 <0.8_alpha-r0
- Alpine:v3.9: `libmspack` — affected >=0 <0.8_alpha-r0

## Details
chmextract.c in the chmextract sample program, as distributed with libmspack before 0.8alpha, does not protect against absolute/relative pathnames in CHM files, leading to Directory Traversal. NOTE: the vendor disputes that this is a libmspack vulnerability, because chmextract.c was only intended as a source-code example, not a supported application

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18586

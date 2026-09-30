# [M] ALPINE-CVE-2020-0499

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-0499
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-0499
Type: osv

## Affected
- Alpine:v3.12: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.13: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.14: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.15: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.16: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.17: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.18: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.19: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.20: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.21: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.22: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.23: `flac` — affected >=0 <1.3.4-r0
- Alpine:v3.24: `flac` — affected >=0 <1.3.4-r0

## Details
In FLAC__bitreader_read_rice_signed_block of bitreader.c, there is a possible out of bounds read due to a heap buffer overflow. This could lead to remote information disclosure with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-11Android ID: A-156076070

## References
- https://security.alpinelinux.org/vuln/CVE-2020-0499

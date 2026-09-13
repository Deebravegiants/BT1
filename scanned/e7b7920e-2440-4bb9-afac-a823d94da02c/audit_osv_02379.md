# [M] ALPINE-CVE-2022-1122

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-1122
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1122
Type: osv

## Affected
- Alpine:v3.16: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.17: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.18: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.19: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.20: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.21: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.22: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.23: `openjpeg` — affected >=0 <2.5.0-r0
- Alpine:v3.24: `openjpeg` — affected >=0 <2.5.0-r0

## Details
A flaw was found in the opj2_decompress program in openjpeg2 2.4.0 in the way it handles an input directory with a large number of files. When it fails to allocate a buffer to store the filenames of the input directory, it calls free() on an uninitialized pointer, leading to a segmentation fault and a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1122

# [M] ALPINE-CVE-2023-2804

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-2804
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2804
Type: osv

## Affected
- Alpine:v3.18: `libjpeg-turbo` — affected >=0 <2.1.5.1-r3
- Alpine:v3.19: `libjpeg-turbo` — affected >=0 <2.1.5.1-r4
- Alpine:v3.20: `libjpeg-turbo` — affected >=0 <2.1.5.1-r4
- Alpine:v3.21: `libjpeg-turbo` — affected >=0 <2.1.5.1-r4
- Alpine:v3.22: `libjpeg-turbo` — affected >=0 <2.1.5.1-r4
- Alpine:v3.23: `libjpeg-turbo` — affected >=0 <2.1.5.1-r4
- Alpine:v3.24: `libjpeg-turbo` — affected >=0 <2.1.5.1-r4

## Details
A heap-based buffer overflow issue was discovered in libjpeg-turbo in h2v2_merged_upsample_internal() function of jdmrgext.c file. The vulnerability can only be exploited with 12-bit data precision for which the range of the sample data type exceeds the valid sample range, hence, an attacker could craft a 12-bit lossless JPEG image that contains out-of-range 12-bit samples. An application attempting to decompress such image using merged upsampling would lead to segmentation fault or buffer overflows, causing an application to crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2804

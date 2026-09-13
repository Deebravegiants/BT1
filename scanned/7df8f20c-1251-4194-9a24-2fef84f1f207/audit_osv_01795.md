# [M] ALPINE-CVE-2020-15389

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-15389
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2020-06-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15389
Type: osv

## Affected
- Alpine:v3.10: `openjpeg` — affected >=0 <2.3.1-r4
- Alpine:v3.11: `openjpeg` — affected >=0 <2.3.1-r4
- Alpine:v3.12: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.13: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.14: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.15: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.16: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.17: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.18: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.19: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.20: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.21: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.22: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.23: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.24: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.9: `openjpeg` — affected >=0 <2.3.0-r6

## Details
jp2/opj_decompress.c in OpenJPEG through 2.3.1 has a use-after-free that can be triggered if there is a mix of valid and invalid files in a directory operated on by the decompressor. Triggering a double-free may also be possible. This is related to calling opj_image_destroy twice.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15389

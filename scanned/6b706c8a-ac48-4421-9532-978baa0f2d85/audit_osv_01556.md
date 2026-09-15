# [H] ALPINE-CVE-2019-2201

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-2201
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-2201
Type: osv

## Affected
- Alpine:v3.10: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.11: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.12: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.13: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.14: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.15: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.16: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.17: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.18: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.19: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.20: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.21: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.22: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.23: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.24: `libjpeg-turbo` — affected >=0 <2.0.4-r0
- Alpine:v3.8: `libjpeg-turbo` — affected >=0 <1.5.3-r6
- Alpine:v3.9: `libjpeg-turbo` — affected >=0 <1.5.3-r6

## Details
In generate_jsimd_ycc_rgb_convert_neon of jsimd_arm64_neon.S, there is a possible out of bounds write due to a missing bounds check. This could lead to remote code execution in an unprivileged process with no additional execution privileges needed. User interaction is needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1 Android-9 Android-10Android ID: A-120551338

## References
- https://security.alpinelinux.org/vuln/CVE-2019-2201

# [M] ALPINE-CVE-2021-0561

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-0561
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-0561
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
In append_to_verify_fifo_interleaved_ of stream_encoder.c, there is a possible out of bounds write due to a missing bounds check. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-11Android ID: A-174302683

## References
- https://security.alpinelinux.org/vuln/CVE-2021-0561

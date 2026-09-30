# [M] ALPINE-CVE-2017-6888

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-6888
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6888
Type: osv

## Affected
- Alpine:v3.10: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.11: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.12: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.13: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.14: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.15: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.16: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.17: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.18: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.19: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.20: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.21: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.22: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.23: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.24: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.8: `flac` — affected >=0 <1.3.2-r2
- Alpine:v3.9: `flac` — affected >=0 <1.3.2-r2

## Details
An error in the "read_metadata_vorbiscomment_()" function (src/libFLAC/stream_decoder.c) in FLAC version 1.3.2 can be exploited to cause a memory leak via a specially crafted FLAC file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6888

# [H] ALPINE-CVE-2017-14160

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-14160
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14160
Type: osv

## Affected
- Alpine:v3.10: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.11: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.12: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.13: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.14: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.15: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.16: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.17: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.18: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.19: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.20: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.21: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.22: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.23: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.24: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.3: `libvorbis` — affected >=0 <1.3.5-r2
- Alpine:v3.4: `libvorbis` — affected >=0 <1.3.5-r2
- Alpine:v3.5: `libvorbis` — affected >=0 <1.3.5-r2
- Alpine:v3.6: `libvorbis` — affected >=0 <1.3.5-r2
- Alpine:v3.7: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.8: `libvorbis` — affected >=0 <1.3.5-r3
- Alpine:v3.9: `libvorbis` — affected >=0 <1.3.5-r3

## Details
The bark_noise_hybridmp function in psy.c in Xiph.Org libvorbis 1.3.5 allows remote attackers to cause a denial of service (out-of-bounds access and application crash) or possibly have unspecified other impact via a crafted mp4 file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14160

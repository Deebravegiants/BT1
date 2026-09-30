# [M] ALPINE-CVE-2017-11548

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-11548
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11548
Type: osv

## Affected
- Alpine:v3.10: `libao` — affected >=0 <1.2.0-r3
- Alpine:v3.11: `libao` — affected >=0 <1.2.0-r3
- Alpine:v3.12: `libao` — affected >=0 <1.2.0-r3
- Alpine:v3.13: `libao` — affected >=0 <1.2.0-r3
- Alpine:v3.14: `libao` — affected >=0 <1.2.0-r3
- Alpine:v3.5: `libao` — affected >=0 <1.2.0-r2
- Alpine:v3.6: `libao` — affected >=0 <1.2.0-r2
- Alpine:v3.7: `libao` — affected >=0 <1.2.0-r2
- Alpine:v3.8: `libao` — affected >=0 <1.2.0-r3
- Alpine:v3.9: `libao` — affected >=0 <1.2.0-r3

## Details
The _tokenize_matrix function in audio_out.c in Xiph.Org libao 1.2.0 allows remote attackers to cause a denial of service (memory corruption) via a crafted MP3 file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11548

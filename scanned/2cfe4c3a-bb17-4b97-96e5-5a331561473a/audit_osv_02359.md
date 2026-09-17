# [H] ALPINE-CVE-2021-46790

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-46790
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-46790
Type: osv

## Affected
- Alpine:v3.16: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.17: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.18: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.19: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.20: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.21: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.22: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.23: `ntfs-3g` — affected >=0 <2022.5.17-r0
- Alpine:v3.24: `ntfs-3g` — affected >=0 <2022.5.17-r0

## Details
ntfsck in NTFS-3G through 2021.8.22 has a heap-based buffer overflow involving buffer+512*3-2. NOTE: the upstream position is that ntfsck is deprecated; however, it is shipped by some Linux distributions.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-46790

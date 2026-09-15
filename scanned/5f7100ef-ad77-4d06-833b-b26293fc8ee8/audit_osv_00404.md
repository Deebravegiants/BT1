# [M] ALPINE-CVE-2017-11550

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-11550
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11550
Type: osv

## Affected
- Alpine:v3.16: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.17: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.18: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.19: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.20: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.21: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.22: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.23: `libid3tag` — affected >=0 <0.16.2-r0
- Alpine:v3.24: `libid3tag` — affected >=0 <0.16.2-r0

## Details
The id3_ucs4_length function in ucs4.c in libid3tag 0.15.1b allows remote attackers to cause a denial of service (NULL Pointer Dereference and application crash) via a crafted mp3 file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11550

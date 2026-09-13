# [H] ALPINE-CVE-2021-3575

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-3575
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3575
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
A heap-based buffer overflow was found in openjpeg in color.c:379:42 in sycc420_to_rgb when decompressing a crafted .j2k file. An attacker could use this to execute arbitrary code with the permissions of the application compiled against openjpeg.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3575

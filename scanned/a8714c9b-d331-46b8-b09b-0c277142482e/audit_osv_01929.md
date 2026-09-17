# [M] ALPINE-CVE-2020-27824

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-27824
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27824
Type: osv

## Affected
- Alpine:v3.10: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.11: `openjpeg` — affected >=0 <2.3.1-r5
- Alpine:v3.12: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.13: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.14: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.15: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.16: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.17: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.18: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.19: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.20: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.21: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.22: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.23: `openjpeg` — affected >=0 <2.3.1-r6
- Alpine:v3.24: `openjpeg` — affected >=0 <2.3.1-r6

## Details
A flaw was found in OpenJPEG’s encoder in the opj_dwt_calc_explicit_stepsizes() function. This flaw allows an attacker who can supply crafted input to decomposition levels to cause a buffer overflow. The highest threat from this vulnerability is to system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27824

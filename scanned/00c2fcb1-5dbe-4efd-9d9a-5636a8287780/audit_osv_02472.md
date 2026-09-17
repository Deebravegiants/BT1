# [M] ALPINE-CVE-2022-25310

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-25310
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-25310
Type: osv

## Affected
- Alpine:v3.16: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.17: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.18: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.19: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.20: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.21: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.22: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.23: `fribidi` — affected >=0 <1.0.12-r0
- Alpine:v3.24: `fribidi` — affected >=0 <1.0.12-r0

## Details
A segmentation fault (SEGV) flaw was found in the Fribidi package and affects the fribidi_remove_bidi_marks() function of the lib/fribidi.c file. This flaw allows an attacker to pass a specially crafted file to Fribidi, leading to a crash and causing a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-25310

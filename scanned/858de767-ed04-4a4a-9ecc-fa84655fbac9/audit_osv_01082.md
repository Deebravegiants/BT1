# [H] ALPINE-CVE-2018-19503

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19503
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19503
Type: osv

## Affected
- Alpine:v3.10: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.11: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.7: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.8: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.9: `faad2` — affected >=0 <2.9.0-r0

## Details
An issue was discovered in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.1. There was a stack-based buffer overflow in the function calculate_gain() in libfaad/sbr_hfadj.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19503

# [H] ALPINE-CVE-2018-20194

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20194
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20194
Type: osv

## Affected
- Alpine:v3.10: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.11: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.7: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.8: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.9: `faad2` — affected >=0 <2.9.0-r0

## Details
There is a stack-based buffer underflow in the third instance of the calculate_gain function in libfaad/sbr_hfadj.c in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. A crafted input will lead to a denial of service or possibly unspecified other impact because limiting the additional noise energy level is mishandled for the G_max <= G case.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20194

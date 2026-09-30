# [H] ALPINE-CVE-2019-10216

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10216
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10216
Type: osv

## Affected
- Alpine:v3.10: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.11: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.12: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.13: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.14: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.15: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.16: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.17: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.18: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.19: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.20: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.21: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.22: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.23: `ghostscript` — affected >=0 <9.27-r2
- Alpine:v3.7: `ghostscript` — affected >=0 <9.26-r3
- Alpine:v3.8: `ghostscript` — affected >=0 <9.26-r3
- Alpine:v3.9: `ghostscript` — affected >=0 <9.26-r3

## Details
In ghostscript before version 9.50, the .buildfont1 procedure did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. An attacker could abuse this flaw by creating a specially crafted PostScript file that could escalate privileges and access files outside of restricted areas.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10216

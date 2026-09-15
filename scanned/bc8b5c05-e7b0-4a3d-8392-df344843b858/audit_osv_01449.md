# [H] ALPINE-CVE-2019-14869

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14869
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14869
Type: osv

## Affected
- Alpine:v3.10: `ghostscript` — affected >=9.00 <9.27-r5
- Alpine:v3.11: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.12: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.13: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.14: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.15: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.16: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.17: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.18: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.19: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.20: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.21: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.22: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.23: `ghostscript` — affected >=9.00 <9.50-r0
- Alpine:v3.9: `ghostscript` — affected >=9.00 <9.26-r5

## Details
A flaw was found in all versions of ghostscript 9.x before 9.50, where the `.charkeys` procedure, where it did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. An attacker could abuse this flaw by creating a specially crafted PostScript file that could escalate privileges within the Ghostscript and access files outside of restricted areas or execute commands.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14869

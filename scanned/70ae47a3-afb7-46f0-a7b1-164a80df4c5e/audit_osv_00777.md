# [H] ALPINE-CVE-2017-8291

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8291
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8291
Type: osv

## Affected
- Alpine:v3.10: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.11: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.12: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.13: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.14: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.15: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.16: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.17: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.18: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.19: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.2: `ghostscript` — affected >=0 <9.21-r0
- Alpine:v3.20: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.21: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.22: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.23: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.3: `ghostscript` — affected >=0 <9.21-r0
- Alpine:v3.4: `ghostscript` — affected >=0 <9.21-r0
- Alpine:v3.5: `ghostscript` — affected >=0 <9.21-r0
- Alpine:v3.6: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.7: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.8: `ghostscript` — affected >=0 <9.21-r2
- Alpine:v3.9: `ghostscript` — affected >=0 <9.21-r2

## Details
Artifex Ghostscript through 2017-04-26 allows -dSAFER bypass and remote command execution via .rsdparams type confusion with a "/OutputFile (%pipe%" substring in a crafted .eps document that is an input to the gs program, as exploited in the wild in April 2017.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8291

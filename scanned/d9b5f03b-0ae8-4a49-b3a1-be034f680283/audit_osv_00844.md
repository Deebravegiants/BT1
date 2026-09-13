# [M] ALPINE-CVE-2018-0360

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-0360
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0360
Type: osv

## Affected
- Alpine:v3.10: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.11: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.12: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.5: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.6: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.7: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.8: `clamav` — affected >=0 <0.100.1-r0
- Alpine:v3.9: `clamav` — affected >=0 <0.100.1-r0

## Details
ClamAV before 0.100.1 has an HWP integer overflow with a resultant infinite loop via a crafted Hangul Word Processor file. This is in parsehwp3_paragraph() in libclamav/hwp.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0360

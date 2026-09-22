# [M] ALPINE-CVE-2017-8374

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-8374
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8374
Type: osv

## Affected
- Alpine:v3.10: `libmad` — affected >=0 <0.15.1b-r9
- Alpine:v3.11: `libmad` — affected >=0 <0.15.1b-r9
- Alpine:v3.7: `libmad` — affected >=0 <0.15.1b-r8
- Alpine:v3.8: `libmad` — affected >=0 <0.15.1b-r9
- Alpine:v3.9: `libmad` — affected >=0 <0.15.1b-r9

## Details
The mad_bit_skip function in bit.c in Underbit MAD libmad 0.15.1b allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted audio file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8374

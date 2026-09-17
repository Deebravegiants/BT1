# [M] ALPINE-CVE-2018-20362

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-20362
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20362
Type: osv

## Affected
- Alpine:v3.10: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.11: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.7: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.8: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.9: `faad2` — affected >=0 <2.9.0-r0

## Details
A NULL pointer dereference was discovered in ifilter_bank of libfaad/filtbank.c in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. The vulnerability causes a segmentation fault and application crash because adding to windowed output is mishandled in the EIGHT_SHORT_SEQUENCE case.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20362

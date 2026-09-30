# [H] ALPINE-CVE-2019-15296

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15296
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15296
Type: osv

## Affected
- Alpine:v3.10: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.11: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.7: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.8: `faad2` — affected >=0 <2.9.0-r0
- Alpine:v3.9: `faad2` — affected >=0 <2.9.0-r0

## Details
An issue was discovered in Freeware Advanced Audio Decoder 2 (FAAD2) 2.8.8. The faad_resetbits function in libfaad/bits.c is affected by a buffer overflow vulnerability. The number of bits to be read is determined by ld->buffer_size - words*4, cast to uint32. If ld->buffer_size - words*4 is negative, a buffer overflow is later performed via getdword_n(&ld->start[words], ld->bytes_left).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15296

# [M] ALPINE-CVE-2017-7697

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7697
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7697
Type: osv

## Affected
- Alpine:v3.2: `libsamplerate` — affected >=0 <0.1.9-r0
- Alpine:v3.3: `libsamplerate` — affected >=0 <0.1.9-r0
- Alpine:v3.4: `libsamplerate` — affected >=0 <0.1.9-r0

## Details
In libsamplerate before 0.1.9, a buffer over-read occurs in the calc_output_single function in src_sinc.c via a crafted audio file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7697

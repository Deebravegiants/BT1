# [H] ALPINE-CVE-2017-6887

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-6887
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6887
Type: osv

## Affected
- Alpine:v3.3: `libraw` — affected >=0 <0.17.2-r1
- Alpine:v3.4: `libraw` — affected >=0 <0.17.2-r1
- Alpine:v3.5: `libraw` — affected >=0 <0.17.2-r1
- Alpine:v3.6: `libraw` — affected >=0 <0.17.2-r1

## Details
A boundary error within the "parse_tiff_ifd()" function (internal/dcraw_common.cpp) in LibRaw versions before 0.18.2 can be exploited to cause a memory corruption via e.g. a specially crafted KDC file with model set to "DSLR-A100" and containing multiple sequences of 0x100 and 0x14A TAGs.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6887

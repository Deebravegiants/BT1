# [C] ALPINE-CVE-2017-6886

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-6886
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6886
Type: osv

## Affected
- Alpine:v3.3: `libraw` — affected >=0 <0.17.2-r1
- Alpine:v3.4: `libraw` — affected >=0 <0.17.2-r1
- Alpine:v3.5: `libraw` — affected >=0 <0.17.2-r1
- Alpine:v3.6: `libraw` — affected >=0 <0.17.2-r1

## Details
An error within the "parse_tiff_ifd()" function (internal/dcraw_common.cpp) in LibRaw versions before 0.18.2 can be exploited to corrupt memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6886

# [H] ALPINE-CVE-2016-9297

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9297
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9297
Type: osv

## Affected
- Alpine:v3.2: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.3: `tiff` — affected >=0 <4.0.7-r0
- Alpine:v3.4: `tiff` — affected >=0 <4.0.7-r0

## Details
The TIFFFetchNormalTag function in LibTiff 4.0.6 allows remote attackers to cause a denial of service (out-of-bounds read) via crafted TIFF_SETGET_C16ASCII or TIFF_SETGET_C32_ASCII tag values.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9297

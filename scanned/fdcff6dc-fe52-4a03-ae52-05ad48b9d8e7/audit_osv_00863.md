# [H] ALPINE-CVE-2018-1000051

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000051
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000051
Type: osv

## Affected
- Alpine:v3.10: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.11: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.7: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.8: `mupdf` — affected >=0 <1.13-r0
- Alpine:v3.9: `mupdf` — affected >=0 <1.13-r0

## Details
Artifex Mupdf version 1.12.0 contains a Use After Free vulnerability in fz_keep_key_storable that can result in DOS / Possible code execution. This attack appear to be exploitable via Victim opens a specially crafted PDF.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000051

# [M] ALPINE-CVE-2026-4367

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-4367
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4367
Type: osv

## Affected
- Alpine:v3.20: `libxpm` — affected >=0 <3.5.19-r0
- Alpine:v3.21: `libxpm` — affected >=0 <3.5.19-r0
- Alpine:v3.22: `libxpm` — affected >=0 <3.5.19-r0
- Alpine:v3.23: `libxpm` — affected >=0 <3.5.19-r0
- Alpine:v3.24: `libxpm` — affected >=0 <3.5.19-r0

## Details
A flaw was found in libXpm. A local user with low privileges could exploit an Out-of-Bounds Read vulnerability in the `xpmNextWord()` function by processing a specially crafted or very small XPM (X PixMap) image file. This improper validation of file boundaries can cause an internal pointer to read beyond the file's end, leading to application crashes and Denial of Service conditions.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4367

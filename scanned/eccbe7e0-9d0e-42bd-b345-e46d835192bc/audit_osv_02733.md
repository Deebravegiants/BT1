# [M] ALPINE-CVE-2022-4645

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-4645
Ecosystem: Alpine:v3.17
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4645
Type: osv

## Affected
- Alpine:v3.17: `tiff` — affected >=0 <4.4.0-r2

## Details
LibTIFF 4.4.0 has an out-of-bounds read in tiffcp in tools/tiffcp.c:948, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit e8131125.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4645

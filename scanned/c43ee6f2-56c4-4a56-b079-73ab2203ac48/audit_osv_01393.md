# [M] ALPINE-CVE-2019-13111

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13111
Ecosystem: Alpine:v3.11
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13111
Type: osv

## Affected
- Alpine:v3.11: `exiv2` — affected >=0 <0.27.2-r0

## Details
A WebPImage::decodeChunks integer overflow in Exiv2 through 0.27.1 allows an attacker to cause a denial of service (large heap allocation followed by a very long running loop) via a crafted WEBP image file.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13111

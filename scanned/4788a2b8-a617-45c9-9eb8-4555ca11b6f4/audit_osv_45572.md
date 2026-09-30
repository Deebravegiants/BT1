# [H] JLSEC-2026-1317

## Summary
Severity: High
Advisory: JLSEC-2026-1317
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1317
Type: osv

## Affected
- Julia: `Exiv2_jll` — affected unspecified

## Details
Exiv2 is a C++ library and a command-line utility to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata. Prior to version 0.28.8, an out-of-bounds read was found in Exiv2. The vulnerability is in the preview component, which is only triggered when running Exiv2 with an extra command line argument, like -pp. The out-of-bounds read is at a 4GB offset, which usually causes Exiv2 to crash. This issue has been patched in version 0.28.8.

## References
- https://github.com/Exiv2/exiv2/commit/eaa9e21aabe06b3f91cfe66686f5ebc3ca3c0ed4
- https://github.com/Exiv2/exiv2/issues/3511
- https://github.com/Exiv2/exiv2/pull/3512
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-3wgv-fg4w-75x7

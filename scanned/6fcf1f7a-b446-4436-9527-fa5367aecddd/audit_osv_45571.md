# [H] JLSEC-2026-1316

## Summary
Severity: High
Advisory: JLSEC-2026-1316
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1316
Type: osv

## Affected
- Julia: `Exiv2_jll` — affected unspecified

## Details
Exiv2 is a C++ library and a command-line utility to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata. Prior to version 0.28.8, an out-of-bounds read was found. The vulnerability is in the CRW image parser. This issue has been patched in version 0.28.8.

## References
- https://github.com/Exiv2/exiv2/commit/cbba4d206512fe63e12d164fdd1881562f072a9d
- https://github.com/Exiv2/exiv2/pull/3462
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-9mxq-4j5g-5wrp

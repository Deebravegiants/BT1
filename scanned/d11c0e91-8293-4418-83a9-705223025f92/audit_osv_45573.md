# [M] JLSEC-2026-1318

## Summary
Severity: Medium
Advisory: JLSEC-2026-1318
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1318
Type: osv

## Affected
- Julia: `Exiv2_jll` — affected unspecified

## Details
Exiv2 is a C++ library and a command-line utility to read, write, delete and modify Exif, IPTC, XMP and ICC image metadata. Prior to version 0.28.8, an uncaught exception was found in Exiv2. The vulnerability is in the preview component, which is only triggered when running Exiv2 with an extra command line argument, like -pp. Due to an integer overflow, the code attempts to create a huge std::vector, which causes Exiv2 to crash with an uncaught exception. This issue has been patched in version 0.28.8.

## References
- https://github.com/Exiv2/exiv2/commit/659db316eef745899a778a1e0b760a971d1b69df
- https://github.com/Exiv2/exiv2/issues/3513
- https://github.com/Exiv2/exiv2/pull/3514
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-p2pw-7935-c73j

# [H] CVE-2020-15908

## Summary
Severity: High
Advisory: CVE-2020-15908
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-23
Source: https://osv.dev/vulnerability/CVE-2020-15908
Type: osv

## Details
tar/TarFileReader.cpp in Cauldron cbang (aka C-Bang or C!) before 1.6.0 allows Directory Traversal during extraction from a TAR archive.

## References
- https://github.com/CauldronDevelopmentLLC/cbang/compare/1.5.1...1.6.0
- https://github.com/CauldronDevelopmentLLC/cbang/commit/1c1dba62bd3e6fa9d0d0c0aa21926043b75382c7

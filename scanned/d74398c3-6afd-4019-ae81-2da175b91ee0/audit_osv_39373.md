# [M] bit7z: Arbitrary File Overwrite via Symlink Attack on Predictable Temp File During Archive Update

## Summary
Severity: Medium
Advisory: CVE-2026-45384
Aliases: GHSA-wjch-42rm-q53h
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45384
Type: osv

## Details
bit7z is a cross-platform C++ static library that allows the compression/extraction of archive files. Prior to version 4.0.12, there is an arbitrary file overwrite vulnerability via symlink attack on predictable temp files during archive update. This issue has been patched in version 4.0.12.

## References
- https://github.com/rikyoz/bit7z/releases/tag/v4.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45384.json
- https://github.com/rikyoz/bit7z/security/advisories/GHSA-wjch-42rm-q53h
- https://nvd.nist.gov/vuln/detail/CVE-2026-45384

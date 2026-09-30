# [M] ImageMagick: Off-by-One in MSL decoder could result in crash

## Summary
Severity: Medium
Advisory: CVE-2026-40312
Aliases: GHSA-5xg3-585r-9jh5
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-40312
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below 7.1.2-19, an off by one error in the MSL decoder could result in a crash when a malicous MSL file is read. This issue has been fixed in version 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40312.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-5xg3-585r-9jh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-40312
- https://github.com/ImageMagick/ImageMagick/commit/2a06c7be3bba3326caf8b7a8d1fa2e0d4b88998d

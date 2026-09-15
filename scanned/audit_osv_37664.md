# [M] ImageMagick has a heap-buffer-overflow in NewXMLTree which could result in crash

## Summary
Severity: Medium
Advisory: CVE-2026-32636
Aliases: GHSA-gc62-2v5p-qpmp
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-32636
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-17 and 6.9.13-42, the NewXMLTree method contains a bug that could result in a crash due to an out of write bounds of a single zero byte. Versions 7.1.2-17 and 6.9.13-42 fix the issue.

## References
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-17
- https://github.com/dlemstra/Magick.NET/releases/tag/14.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32636.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-gc62-2v5p-qpmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32636

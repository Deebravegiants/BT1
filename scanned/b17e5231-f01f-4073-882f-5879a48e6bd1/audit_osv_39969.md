# [M] ImageMagick: Stack Overflow in MVG decoder

## Summary
Severity: Medium
Advisory: CVE-2026-48734
Aliases: GHSA-h36c-3666-h489
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-48734
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-49 and 7.1.2-24, a crafted MVG file could result in a stack overflow due to a missing depth or visited-set check. This issue has been patched in versions 6.9.13-49 and 7.1.2-24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48734.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-h36c-3666-h489
- https://nvd.nist.gov/vuln/detail/CVE-2026-48734

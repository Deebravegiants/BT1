# [M] ImageMagick: Stack buffer overflow in XTileImage

## Summary
Severity: Medium
Advisory: CVE-2026-42050
Aliases: GHSA-7mxf-ff4f-jj7p
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42050
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-21 and 6.9.13-46, a malicious MIFF file could trigger an overflow when a user opens it in the display tool and right-clicks a tile to invoke the Load / Update menu item. This vulnerability is fixed in 7.1.2-21 and 6.9.13-46.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42050.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7mxf-ff4f-jj7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-42050

# [M] ImageMagick: Converting multi-layer nested MVG to SVG can cause DoS

## Summary
Severity: Medium
Advisory: CVE-2026-24484
Aliases: GHSA-wg3g-gvx5-2pmv
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-24484
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-15 and 6.9.13-40, Magick fails to check for multi-layer nested mvg conversions to svg, leading to DoS. Versions 7.1.2-15 and 6.9.13-40 contain a patch.

## References
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24484.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wg3g-gvx5-2pmv
- https://nvd.nist.gov/vuln/detail/CVE-2026-24484
- https://github.com/ImageMagick/ImageMagick/commit/0349df6d43d633bd61bb582d1e1e87d6332de32a

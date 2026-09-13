# [H] JLSEC-2026-1051

## Summary
Severity: High
Advisory: JLSEC-2026-1051
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1051
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick before 7.1.2-19 contains an out-of-bounds access vulnerability in ConnectedComponentsImage() when processing connected-components artifacts with invalid indices. Attackers can trigger access violations by specifying malformed connected-components definitions via CLI, causing denial of service or potential code execution.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-pmpg-6pww-fg6q
- https://www.vulncheck.com/advisories/imagemagick-out-of-bounds-access-in-connectedcomponentsimage-via-connected-components-artifact

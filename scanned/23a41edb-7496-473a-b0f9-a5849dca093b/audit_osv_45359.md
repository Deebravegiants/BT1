# [M] ImageMagick before 7.1.2-26 and 6.9.13-51 is missing a check for the allowed memory allocation...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1062
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1062
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick before 7.1.2-26 and 6.9.13-51 is missing a check for the allowed memory allocation limit in matrix-backed operations such as -canny. An attacker can supply a crafted image that causes ImageMagick to allocate more memory than permitted by the configured policy, resulting in a denial of service.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-rvhp-75f6-9jqh
- https://github.com/advisories/GHSA-84wp-3vxv-vr3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-61465
- https://www.vulncheck.com/advisories/imagemagick-before-26-memory-allocation-policy-bypass

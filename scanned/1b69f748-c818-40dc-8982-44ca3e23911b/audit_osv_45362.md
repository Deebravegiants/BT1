# [H] ImageMagick before 7.1.2-26 contains a use-after-free vulnerability in the FormatMagickCaption...

## Summary
Severity: High
Advisory: JLSEC-2026-1067
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1067
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick before 7.1.2-26 contains a use-after-free vulnerability in the FormatMagickCaption method when memory allocation fails. Attackers can trigger memory allocation failures to cause a dangling pointer to reference freed memory, potentially enabling denial of service or code execution.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qvxh-prvr-85w2
- https://github.com/advisories/GHSA-vg96-jmxw-665f
- https://nvd.nist.gov/vuln/detail/CVE-2026-61861
- https://www.vulncheck.com/advisories/imagemagick-before-26-use-after-free-in-formatmagickcaption

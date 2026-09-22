# [H] JLSEC-2026-933

## Summary
Severity: High
Advisory: JLSEC-2026-933
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-933
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-12, in the WriteSVGImage function, using an int variable to store `number_attributes` caused an integer overflow. This, in turn, triggered a buffer overflow and caused a DoS attack. Version 7.1.2-12 fixes the issue.

## References
- https://github.com/ImageMagick/ImageMagick/commit/2c08c2311693759153c9aa99a6b2dcb5f985681e
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-hrh7-j8q2-4qcw

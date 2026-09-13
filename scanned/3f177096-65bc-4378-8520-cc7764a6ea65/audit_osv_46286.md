# [M] JLSEC-2026-920

## Summary
Severity: Medium
Advisory: JLSEC-2026-920
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-920
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2001+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-1, when preparing to transform from Log to sRGB colorspaces, the logmap construction fails to handle cases where the reference-black or reference-white value is larger than 1024. This leads to corrupting memory beyond the end of the allocated logmap buffer. This issue has been patched in version 7.1.2-1.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-v393-38qx-v8fp
- https://goo.gle/bigsleep

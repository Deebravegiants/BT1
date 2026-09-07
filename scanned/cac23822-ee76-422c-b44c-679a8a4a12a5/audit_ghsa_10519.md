# [M] ImageMagick has an integer overflow in despeckle operation causing a heap buffer overflow on 32-bit builds

## Summary
Severity: Medium
Advisory: GHSA-26qp-ffjh-2x4v
CVE: CVE-2026-34238
CWE: CWE-190, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-26qp-ffjh-2x4v
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.12.0

## Details
An integer overflow in the despeckle operation causes a heap buffer overflow on 32-bit builds that will result in an out of bounds write.

```
==1551685==ERROR: AddressSanitizer: heap-buffer-overflow on address 0xea2fb818 at pc 0x56cbc42a bp 0xffc4ce48 sp 0xffc4ce38
WRITE of size 8 at 0xea2fb818 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-26qp-ffjh-2x4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34238
- https://github.com/ImageMagick/ImageMagick/commit/bcd8519c70ecd9ebbc180920f2cf97b267d1f440
- https://github.com/ImageMagick/ImageMagick
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0

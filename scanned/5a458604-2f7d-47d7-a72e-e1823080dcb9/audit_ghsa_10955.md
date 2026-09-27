# [M] ImageMagick has an Out-of-bounds Write via InterpretImageFilename

## Summary
Severity: Medium
Advisory: GHSA-8793-7xv6-82cf
CVE: CVE-2026-33536
CWE: CWE-121, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-8793-7xv6-82cf
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.11.1
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.11.1

## Details
Due to an incorrect return value on certain platforms a pointer is incremented past the end of a buffer that is on the stack and that could result in an out of bounds write.

```
=================================================================
==48558==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x00016b9b7490 at pc 0x0001046d48ac bp 0x00016b9b31d0 sp 0x00016b9b31c8
WRITE of size 1 at 0x00016b9b7490 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8793-7xv6-82cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-33536
- https://github.com/ImageMagick/ImageMagick

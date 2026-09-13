# [M] ImageMagick: Heap Buffer Over-read in WaveletDenoise when processing small images

## Summary
Severity: Medium
Advisory: GHSA-qpgx-jfcq-r59f
CVE: CVE-2026-27798
CWE: CWE-125, CWE-126
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-qpgx-jfcq-r59f
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
A heap buffer over-read vulnerability occurs when processing an image with small dimension using the `-wavelet-denoise` operator.

```
==3693336==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x511000001280 at pc 0x5602c8b0cc75 bp 0x7ffcb105d510 sp 0x7ffcb105d500
READ of size 4 at 0x511000001280 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qpgx-jfcq-r59f
- https://nvd.nist.gov/vuln/detail/CVE-2026-27798
- https://github.com/ImageMagick/ImageMagick/commit/0377e60b3c0d766bd7271221c95d9ee54f6a3738
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

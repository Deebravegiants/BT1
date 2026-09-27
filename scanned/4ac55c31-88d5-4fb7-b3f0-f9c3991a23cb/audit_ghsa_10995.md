# [M] ImageMagick has heap buffer overflow in YUV 4:2:2 decoder

## Summary
Severity: Medium
Advisory: GHSA-mqfc-82jx-3mr2
CVE: CVE-2026-25986
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-mqfc-82jx-3mr2
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
A heap buffer overflow write vulnerability exists in ReadYUVImage() (coders/yuv.c) when processing malicious YUV 4:2:2 (NoInterlace) images. The pixel-pair loop writes one pixel beyond the allocated row buffer.

```
=================================================================
==204642==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x5170000002e0 at pc 0x562d21a7e8de bp 0x7fffa9ae1270 sp 0x7fffa9ae1260
WRITE of size 8 at 0x5170000002e0 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-mqfc-82jx-3mr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25986
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

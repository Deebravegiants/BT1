# [M] ImageMagick has heap use-after-free in the MSL encoder

## Summary
Severity: Medium
Advisory: GHSA-xxw5-m53x-j38c
CVE: CVE-2026-28688
CWE: CWE-416
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-xxw5-m53x-j38c
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.4

## Details
A heap-use-after-free vulnerability exists in the MSL encoder, where a cloned image is destroyed twice. The MSL coder does not support writing MSL so the write capability has been removed. 

```
SUMMARY: AddressSanitizer: heap-use-after-free MagickCore/image.c:1195 in DestroyImage
Shadow bytes around the buggy address:
  0x0a4e80007450: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0a4e80007460: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0a4e80007470: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0a4e80007480: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0a4e80007490: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
=>0x0a4e800074a0: fd fd fd fd fd fd fd fd fd fd[fd]fd fd fd fd fd
  0x0a4e800074b0: fd fd fd fd fd fd fd fd fd fa fa fa fa fa fa fa
  0x0a4e800074c0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0a4e800074d0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0a4e800074e0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0a4e800074f0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xxw5-m53x-j38c
- https://nvd.nist.gov/vuln/detail/CVE-2026-28688
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.4

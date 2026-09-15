# [M] ImageMagick: Memory Leak in multiple coders that write raw pixel data 

## Summary
Severity: Medium
Advisory: GHSA-wfx3-6g53-9fgc
CVE: CVE-2026-56368
CWE: CWE-401
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-wfx3-6g53-9fgc
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
A memory leak vulnerability exists in multiple coders that write raw pixel data where an object is not freed. 

```
Direct leak of 160 byte(s) in 1 object(s) allocated from:
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wfx3-6g53-9fgc
- https://nvd.nist.gov/vuln/detail/CVE-2026-56368
- https://github.com/ImageMagick/ImageMagick/commit/fe0a49a58ac5b7a18ff2618b6207dcad71123e43
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3
- https://www.vulncheck.com/advisories/imagemagick-memory-leak-in-raw-pixel-data-coders

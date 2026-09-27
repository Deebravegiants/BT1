# [M] ImageMagick has memory leak of watermark Image object in ReadSTEGANOImage on multiple error/early-return paths

## Summary
Severity: Medium
Advisory: GHSA-g2pr-qxjg-7r2w
CVE: CVE-2026-25796
CWE: CWE-401
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-g2pr-qxjg-7r2w
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
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
### Summary

In `ReadSTEGANOImage()` (`coders/stegano.c`), the `watermark` Image object is not freed on three early-return paths, resulting in a definite memory leak (~13.5KB+ per invocation) that can be exploited for denial of service.

```
Direct leak of 13512 byte(s) in 1 object(s) allocated from:
    #0 0x7f5c11e27887 in __interceptor_malloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:145
    #1 0x55cdc38f65c4 in AcquireMagickMemory MagickCore/memory.c:536
    #2 0x55cdc38f65eb in AcquireCriticalMemory MagickCore/memory.c:612
    #3 0x55cdc3899e91 in AcquireImage MagickCore/image.c:154
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-g2pr-qxjg-7r2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-25796
- https://github.com/ImageMagick/ImageMagick/commit/93ad259ce4f6d641eea0bee73f374af90f35efc3
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

# [M] ImageMagick has NULL Pointer Dereference in ClonePixelCacheRepository via crafted image

## Summary
Severity: Medium
Advisory: GHSA-p863-5fgm-rgq4
CVE: CVE-2026-25798
CWE: CWE-476
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-p863-5fgm-rgq4
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
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
A NULL pointer dereference in ClonePixelCacheRepository allows a remote attacker to crash any application linked against ImageMagick by supplying a crafted image file, resulting in Denial of Service.

```
AddressSanitizer:DEADLYSIGNAL
=================================================================
==3704942==ERROR: AddressSanitizer: UNKNOWN SIGNAL on unknown address 0x000000000000 (pc 0x7f9d141239e0 bp 0x7ffd4c5711e0 sp 0x7ffd4c571148 T0)
    #0 0x7f9d141239e0  (/lib/x86_64-linux-gnu/libc.so.6+0xc49e0)
    #1 0x558a25e4f08d in ClonePixelCacheRepository._omp_fn.0 MagickCore/cache.c:784
    #2 0x7f9d14c06a15 in GOMP_parallel (/lib/x86_64-linux-gnu/libgomp.so.1+0x14a15)
    #3 0x558a25e43151 in ClonePixelCacheRepository MagickCore/cache.c:753
    #4 0x558a25e49a96 in OpenPixelCache MagickCore/cache.c:3849
    #5 0x558a25e45117 in GetImagePixelCache MagickCore/cache.c:1829
    #6 0x558a25e4dde3 in SyncImagePixelCache MagickCore/cache.c:5647
    #7 0x558a256ba57d in SetImageExtent MagickCore/image.c:2713
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-p863-5fgm-rgq4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25798
- https://github.com/ImageMagick/ImageMagick/issues/8567
- https://github.com/ImageMagick/ImageMagick/commit/e046417675d5c26e5f48816851a406c121c77469
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

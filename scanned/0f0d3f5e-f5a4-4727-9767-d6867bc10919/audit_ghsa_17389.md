# [M] ImageMagick's failure to limit MVG mutual causes Stack Overflow

## Summary
Severity: Medium
Advisory: GHSA-7rvh-xqp3-pr8j
CVE: CVE-2025-68950
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-12-30
Source: https://github.com/advisories/GHSA-7rvh-xqp3-pr8j
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.1
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.1

## Details
### Summary
Magick fails to check for circular references between two MVGs, leading to a stack overflow.

### Details

After reading mvg1 using Magick, the following is displayed:
```
./magick -limit memory 2GiB -limit map 2GiB -limit disk 0 mvg:L1.mvg out.png
AddressSanitizer:DEADLYSIGNAL
=================================================================
==3564123==ERROR: AddressSanitizer: UNKNOWN SIGNAL on unknown address 0x000000000000 (pc 0x5589549a4458 bp 0x7ffcc61f34a0 sp 0x7ffcc61efdd0 T0)
    #0 0x5589549a4458 in GetImagePixelCache MagickCore/cache.c:1726
    #1 0x5589549b02c1 in QueueAuthenticPixelCacheNexus MagickCore/cache.c:4261
    #2 0x5589549a2f24 in GetAuthenticPixelCacheNexus MagickCore/cache.c:1368
    #3 0x5589549bae98 in GetCacheViewAuthenticPixels MagickCore/cache-view.c:311
    #4 0x558954afb3a5 in DrawPolygonPrimitive._omp_fn.1 MagickCore/draw.c:5172
    #5 0x7f62dd89fa15 in GOMP_parallel (/lib/x86_64-linux-gnu/libgomp.so.1+0x14a15)
    #6 0x558954ae0f41 in DrawPolygonPrimitive MagickCore/draw.c:5156
    #7 0x558954ae5607 in DrawPrimitive MagickCore/draw.c:5875
    #8 0x558954adc72d in RenderMVGContent MagickCore/draw.c:4522
    #9 0x558954adcf67 in DrawImage MagickCore/draw.c:4561
    #10 0x55895496cedb in RenderFreetype MagickCore/annotate.c:2065
    #11 0x55895496702e in RenderType MagickCore/annotate.c:1112
    #12 0x558954963da7 in AnnotateImage MagickCore/annotate.c:544
    #13 0x558954ae4e0a in DrawPrimitive MagickCore/draw.c:5799
    #14 0x558954adc72d in RenderMVGContent MagickCore/draw.c:4522
    #15 0x558954adcf67 in DrawImage MagickCore/draw.c:4561
    #16 0x558954755a46 in ReadMVGImage coders/mvg.c:240
    #17 0x558954a15ecc in ReadImage MagickCore/constitute.c:743
    #18 0x558954ae3c76 in DrawPrimitive MagickCore/draw.c:5705
    #19 0x558954adc72d in RenderMVGContent MagickCore/draw.c:4522
    #20 0x558954adcf67 in DrawImage MagickCore/draw.c:4561
    #21 0x558954755a46 in ReadMVGImage coders/mvg.c:240
    ...
```

### Impact
This is a DoS vulnerability, and any situation that allows reading the mvg file will be affected.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7rvh-xqp3-pr8j
- https://nvd.nist.gov/vuln/detail/CVE-2025-68950
- https://github.com/ImageMagick/ImageMagick/commit/204718c2211903949dcfc0df8e65ed066b008dec
- https://github.com/ImageMagick/ImageMagick

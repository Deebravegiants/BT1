# [M] ImageMagick has Division-by-Zero in YUV sampling factor validation, which leads to crash

## Summary
Severity: Medium
Advisory: GHSA-543g-8grm-9cw6
CVE: CVE-2026-25799
CWE: CWE-369
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-543g-8grm-9cw6
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
A logic error in YUV sampling factor validation allows an invalid sampling factor to bypass checks and trigger a division-by-zero during image loading, resulting in a reliable denial-of-service.

```
coders/yuv.c:210:47: runtime error: division by zero
AddressSanitizer:DEADLYSIGNAL
=================================================================
==3543373==ERROR: AddressSanitizer: UNKNOWN SIGNAL on unknown address 0x000000000000 (pc 0x55deeb4d723c bp 0x7fffc28d34d0 sp 0x7fffc28d3320 T0)
    #0 0x55deeb4d723c in ReadYUVImage coders/yuv.c:210
    #1 0x55deeb751dff in ReadImage MagickCore/constitute.c:743
    #2 0x55deeb756374 in ReadImages MagickCore/constitute.c:1082
    #3 0x55deec682375 in CLINoImageOperator MagickWand/operation.c:4959
    #4 0x55deec6887ed in CLIOption MagickWand/operation.c:5473
    #5 0x55deec32843b in ProcessCommandOptions MagickWand/magick-cli.c:653
    #6 0x55deec32b99b in MagickImageCommand MagickWand/magick-cli.c:1392
    #7 0x55deec324d58 in MagickCommandGenesis MagickWand/magick-cli.c:177
    #8 0x55deead82519 in MagickMain utilities/magick.c:162
    #9 0x55deead828be in main utilities/magick.c:193
    #10 0x7fb90807fd8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #11 0x7fb90807fe3f in __libc_start_main_impl ../csu/libc-start.c:392
    #12 0x55deead81974 in _start (/data/ylwang/LargeScan/targets/ImageMagick/utilities/magick+0x22fb974)

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: UNKNOWN SIGNAL coders/yuv.c:210 in ReadYUVImage
==3543373==ABORTING
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-543g-8grm-9cw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-25799
- https://github.com/ImageMagick/ImageMagick/commit/49000e7298fbfdd759ac2c46f740f40c2e9b7452
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

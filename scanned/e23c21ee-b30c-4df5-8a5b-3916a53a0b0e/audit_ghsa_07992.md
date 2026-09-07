# [M] ImageMagick has memory leak in msl encoder

## Summary
Severity: Medium
Advisory: GHSA-gxcx-qjqp-8vjw
CVE: CVE-2026-25638
CWE: CWE-401
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-gxcx-qjqp-8vjw
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
- NuGet: `Magick.NET-Q8-x86.NET-Q8-x64` — affected >=0 <14.10.3

## Details
Memory leak exists in `coders/msl.c`. In the `WriteMSLImage` function of the `msl.c` file, resources are allocated. But the function returns early without releasing these allocated resources. 

```
==78983== Memcheck, a memory error detector
==78983== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==78983== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==78983== 
==78983== 177,196 (13,512 direct, 163,684 indirect) bytes in 1 blocks are definitely lost in loss record 21 of 21
==78983==    at 0x4846828: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-amd64-linux.so)
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-gxcx-qjqp-8vjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-25638
- https://github.com/ImageMagick/ImageMagick/commit/1e88fca11c7b8517100d518bc99bd8c474f02f88
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

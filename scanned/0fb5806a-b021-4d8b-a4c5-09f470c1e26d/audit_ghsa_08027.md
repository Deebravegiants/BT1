# [M] Image Magick has a Memory Leak in coders/ashlar.c

## Summary
Severity: Medium
Advisory: GHSA-xgm3-v4r9-wfgm
CVE: CVE-2026-25969
CWE: CWE-401
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-xgm3-v4r9-wfgm
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
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
Memory leak exists in `coders/ashlar.c`. The `WriteASHLARImage` allocates a structure.  However, when an exception is thrown, the allocated memory is not properly released, resulting in a potential memory leak.

```
```bash
==78968== Memcheck, a memory error detector
==78968== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==78968== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==78968== 
==78968== HEAP SUMMARY:
==78968==     in use at exit: 17,232 bytes in 4 blocks
==78968==   total heap usage: 4,781 allocs, 4,777 frees, 785,472 bytes allocated
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xgm3-v4r9-wfgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25969
- https://github.com/ImageMagick/ImageMagick/commit/a253d1b124ebdcc2832daac6f9a35c362635b40e
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

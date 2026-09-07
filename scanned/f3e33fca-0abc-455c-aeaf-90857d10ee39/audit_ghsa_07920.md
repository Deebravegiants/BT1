# [M] ImageMagick: Possible memory leak in ASHLAR encoder

## Summary
Severity: Medium
Advisory: GHSA-gm37-qx7w-p258
CVE: CVE-2026-25637
CWE: CWE-401
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-gm37-qx7w-p258
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
A memory leak in the ASHLAR image writer allows an attacker to exhaust process memory by providing a crafted image that results in small objects that are allocated but never freed.

```
==880062== Memcheck, a memory error detector
==880062== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==880062== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==880062== 
==880062== 
==880062== HEAP SUMMARY:
==880062==     in use at exit: 386,826 bytes in 696 blocks
==880062==   total heap usage: 30,523 allocs, 29,827 frees, 21,803,756 bytes allocated
==880062== 
==880062== LEAK SUMMARY:
==880062==    definitely lost: 3,408 bytes in 3 blocks
==880062==    indirectly lost: 88,885 bytes in 30 blocks
==880062==      possibly lost: 140,944 bytes in 383 blocks
==880062==    still reachable: 151,573 bytes in 259 blocks
==880062==         suppressed: 0 bytes in 0 blocks
==880062== Reachable blocks (those to which a pointer was found) are not shown.
==880062== To see them, rerun with: --leak-check=full --show-leak-kinds=all
==880062== 
==880062== For lists of detected and suppressed errors, rerun with: -s
==880062== ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-gm37-qx7w-p258
- https://nvd.nist.gov/vuln/detail/CVE-2026-25637
- https://github.com/ImageMagick/ImageMagick/commit/30ce0e8efbd72fd6b50ed3a10ae22f57c8901137
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

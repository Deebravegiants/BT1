# [M] ImageMagick has NULL pointer dereference in ReadSFWImage after DestroyImageInfo (sfw.c)

## Summary
Severity: Medium
Advisory: GHSA-p33r-fqw2-rqmm
CVE: CVE-2026-25795
CWE: CWE-476
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-p33r-fqw2-rqmm
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
In `ReadSFWImage()` (`coders/sfw.c`), when temporary file creation fails, `read_info` is destroyed before its `filename` member is accessed, causing a NULL pointer dereference and crash.

```
AddressSanitizer:DEADLYSIGNAL
=================================================================
==1414421==ERROR: AddressSanitizer: UNKNOWN SIGNAL on unknown address 0x000000000000 (pc 0x56260222912f bp 0x7ffec0a193b0 sp 0x7ffec0a19360 T0)
    #0 0x56260222912f  (/data/ylwang/LargeScan/targets/ImageMagick/utilities/magick+0x235f12f)
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-p33r-fqw2-rqmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25795
- https://github.com/ImageMagick/ImageMagick/commit/332c1566acc2de77857032d3c2504ead6210ff50
- https://github.com/ImageMagick/ImageMagick/commit/55c344f4b514213642da41194bab57b4476fb9f5
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

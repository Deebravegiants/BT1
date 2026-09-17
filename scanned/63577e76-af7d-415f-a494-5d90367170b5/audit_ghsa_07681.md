# [M] ImageMagick: Heap overflow in sun decoder on 32-bit systems may result in out of bounds write

## Summary
Severity: Medium
Advisory: GHSA-6j5f-24fw-pqp4
CVE: CVE-2026-25897
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-6j5f-24fw-pqp4
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
An Integer Overflow vulnerability exists in the sun decoder. On 32-bit systems/builds, a carefully crafted image can lead to an out of bounds heap write.

```
=================================================================
==1967675==ERROR: AddressSanitizer: heap-buffer-overflow on address 0xf190b50e at pc 0x5eae8777 bp 0xffb0fdd8 sp 0xffb0fdd0
WRITE of size 1 at 0xf190b50e thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-6j5f-24fw-pqp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25897
- https://github.com/ImageMagick/ImageMagick/commit/23fde73188ea32c15b607571775d4f92bdb75e60
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

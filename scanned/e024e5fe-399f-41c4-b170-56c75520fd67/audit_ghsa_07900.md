# [H] ImageMagick has heap-buffer-overflow via signed integer overflow in WriteUHDRImage when writing UHDR images with large dimensions

## Summary
Severity: High
Advisory: GHSA-vhqj-f5cj-9x8h
CVE: CVE-2026-25794
CWE: CWE-122, CWE-190
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-vhqj-f5cj-9x8h
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
`WriteUHDRImage` in `coders/uhdr.c` uses `int` arithmetic to compute the pixel buffer size. When image dimensions are large, the multiplication overflows 32-bit `int`, causing an undersized heap allocation followed by an out-of-bounds write. This can crash the process or potentially lead to an out of bounds heap write.
```
==1575126==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x7fc382ef3820 at pc 0x5560d31f229f bp 0x7ffe865f9530 sp 0x7ffe865f9520
WRITE of size 8 at 0x7fc382ef3820 thread T0
    #0 0x5560d31f229e in WriteUHDRImage coders/uhdr.c:807
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-vhqj-f5cj-9x8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25794
- https://github.com/ImageMagick/ImageMagick/commit/ffe589df5ff8ce1433daa4ccb0d2a9fadfbe30ed
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

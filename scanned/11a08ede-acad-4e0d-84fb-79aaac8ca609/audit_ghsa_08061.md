# [H] ImageMagick has Possible Heap Information Disclosure in PSD ZIP Decompression

## Summary
Severity: High
Advisory: GHSA-96pc-27rx-pr36
CVE: CVE-2026-24481
CWE: CWE-125
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-96pc-27rx-pr36
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
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
### Description
A heap information disclosure vulnerability exists in ImageMagick's PSD (Adobe Photoshop) format handler. When processing a maliciously crafted PSD file containing ZIP-compressed layer data that decompresses to less than the expected size, uninitialized heap memory is leaked into the output image.

### Expected Impact
Information disclosure leading to potential exposure of sensitive data from server memory.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-96pc-27rx-pr36
- https://nvd.nist.gov/vuln/detail/CVE-2026-24481
- https://github.com/ImageMagick/ImageMagick/commit/51c9d33f4770cdcfa1a029199375d570af801c97
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

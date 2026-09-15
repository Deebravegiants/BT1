# [M] ImageMagick: Heap Buffer Over-Read of a 4 bytes in distort operation.

## Summary
Severity: Medium
Advisory: GHSA-pfvh-m9xv-8966
CVE: CVE-2026-45624
CWE: CWE-125, CWE-129
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-pfvh-m9xv-8966
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.13.1

## Details
When performing a polynomial distortion an out of bounds over-read of 24 bytes can occur when specifying specific arguments.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-pfvh-m9xv-8966
- https://nvd.nist.gov/vuln/detail/CVE-2026-45624
- https://github.com/ImageMagick/ImageMagick

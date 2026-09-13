# [M] ImageMagick releases an invalid pointer in BilateralBlur when memory allocation fails

## Summary
Severity: Medium
Advisory: GHSA-39h3-g67r-7g3c
CVE: CVE-2026-22770
CWE: CWE-763
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-39h3-g67r-7g3c
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.2
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.2

## Details
The BilateralBlurImage method will allocate a set of double buffers inside AcquireBilateralTLS. But the last element in the set is not properly initialized. This will result in a release of an invalid pointer inside DestroyBilateralTLS when the memory allocation fails.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-39h3-g67r-7g3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-22770
- https://github.com/ImageMagick/ImageMagick/commit/3e0330721020e0c5bb52e4b77c347527dd71658e
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.2

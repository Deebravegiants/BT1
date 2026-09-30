# [M] ImageMagick: Write heap-buffer-overflow in PCL encoder via undersized output buffer

## Summary
Severity: Medium
Advisory: GHSA-467j-76j7-5885
CVE: CVE-2026-28686
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-467j-76j7-5885
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.4

## Details
A heap-buffer-overflow vulnerability exists in the PCL encode due to an undersized output buffer allocation.

```
WRITE of size 1 at 0x7e79f91f31a0 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-467j-76j7-5885
- https://nvd.nist.gov/vuln/detail/CVE-2026-28686
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.4

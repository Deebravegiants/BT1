# [M] ImageMagick has Global Buffer Overflow (OOB Read) via Negative Pixel Index in UIL and XPM Writer

## Summary
Severity: Medium
Advisory: GHSA-vpxv-r9pg-7gpr
CVE: CVE-2026-25898
CWE: CWE-125
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-vpxv-r9pg-7gpr
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
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
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
The UIL and XPM image encoder do not validate the pixel index value returned by `GetPixelIndex()` before using it as an array subscript. In HDRI builds, `Quantum` is a floating-point type, so pixel index values can be negative. An attacker can craft an image with negative pixel index values to trigger a global buffer overflow read during conversion, leading to information disclosure or a process crash.

```
READ of size 1 at 0x55a8823a776e thread T0
    #0 0x55a880d01e85 in WriteUILImage coders/uil.c:355
```

```
READ of size 1 at 0x55fa1c04c66e thread T0
    #0 0x55fa1a9ee415 in WriteXPMImage coders/xpm.c:1135
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-vpxv-r9pg-7gpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25898
- https://github.com/ImageMagick/ImageMagick/commit/c9c87dbaba56bf82aebd3392e11f0ffd93709b12
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

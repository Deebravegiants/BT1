# [H] ImageMagick: Stack buffer overflow in FTXT reader via oversized integer field

## Summary
Severity: High
Advisory: GHSA-72hf-fj62-w6j4
CVE: CVE-2026-25967
CWE: CWE-121
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-72hf-fj62-w6j4
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
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `agick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
### Summary
A stack-based buffer overflow exists in the ImageMagick FTXT image reader. A crafted FTXT file can cause out-of-bounds writes on the stack, leading to a crash.

```
=================================================================
==3537074==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffee4850ef0 at pc 0x5607c408fb33 bp 0x7ffee484fe50 sp 0x7ffee484fe40
WRITE of size 1 at 0x7ffee4850ef0 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-72hf-fj62-w6j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25967
- https://github.com/ImageMagick/ImageMagick/commit/9afe96cc325da1e4349fbd7418675af2f8708c10
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

# [M] ImageMagick has stack write buffer overflow in MNG encoder

## Summary
Severity: Medium
Advisory: GHSA-7h7q-j33q-hvpf
CVE: CVE-2026-28690
CWE: CWE-121
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-7h7q-j33q-hvpf
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
A stack buffer overflow vulnerability exists in the MNG encoder. There is a bounds checks missing that could corrupting the stack with attacker-controlled data.

```
==2265506==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffec4971310 at pc 0x55e671b8a072 bp 0x7ffec4970f70 sp 0x7ffec4970f68
WRITE of size 1 at 0x7ffec4971310 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7h7q-j33q-hvpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28690
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.4

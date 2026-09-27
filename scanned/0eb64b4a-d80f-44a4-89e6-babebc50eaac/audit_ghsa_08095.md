# [M] ImageMagick: Code Injection via PostScript header in ps coders

## Summary
Severity: Medium
Advisory: GHSA-rw6c-xp26-225v
CVE: CVE-2026-25797
CWE: CWE-94
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-rw6c-xp26-225v
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.3
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
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.3

## Details
The ps encoders, responsible for writing PostScript files, fails to sanitize the input before writing it into the PostScript header.  An attacker can provide a malicious file and inject arbitrary PostScript code. When the resulting file is processed by a printer or a viewer (like Ghostscript), the injected code is interpreted and executed.

The html encoder does not properly escape strings that are written to in the html document. An attacker can provide a malicious file and injection arbitrary html code.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-rw6c-xp26-225v
- https://nvd.nist.gov/vuln/detail/CVE-2026-25797
- https://github.com/ImageMagick/ImageMagick/commit/26088a83d71e9daa203d54a56fe3c31f3f85463d
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

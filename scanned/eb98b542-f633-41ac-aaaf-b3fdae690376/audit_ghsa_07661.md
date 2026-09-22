# [H] ImageMagick: Policy bypass through path traversal allows reading restricted content despite secured policy

## Summary
Severity: High
Advisory: GHSA-8jvj-p28h-9gm7
CVE: CVE-2026-25965
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-8jvj-p28h-9gm7
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
ImageMagick’s path security policy is enforced on the raw filename string before the filesystem resolves it. As a result, a policy rule such as /etc/* can be bypassed by a path traversal. The OS resolves the traversal and opens the sensitive file, but the policy matcher only sees the unnormalized path and therefore allows the read. This enables local file disclosure (LFI) even when policy-secure.xml is applied.

Actions to prevent reading from files have been taken. But it make sure writing is also not possible the following should be added to your policy:

```
<policy domain="path" rights="none" pattern="*../*"/>
```

And this will also be included in the project's more secure policies by default.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8jvj-p28h-9gm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25965
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

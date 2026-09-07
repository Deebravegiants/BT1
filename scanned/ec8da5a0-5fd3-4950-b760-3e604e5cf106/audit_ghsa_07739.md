# [M] ImageMagick's Security Policy Bypass through config/policy-secure.xml via "fd handler" leads to stdin/stdout access

## Summary
Severity: Medium
Advisory: GHSA-xwc6-v6g8-pw2h
CVE: CVE-2026-25966
CWE: CWE-284
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-xwc6-v6g8-pw2h
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-QMagick.NET-Q16-x8616-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
The shipped “secure” security policy includes a rule intended to prevent reading/writing from standard streams:

```xml
<policy domain="path" rights="none" pattern="-"/>
```

However, ImageMagick also supports fd:<n> pseudo-filenames (e.g., fd:0, fd:1). This path form is not blocked by the secure policy templates, and therefore bypasses the protection goal of “no stdin/stdout”.

To resolve this, users can add the following change to their security policy.

```xml
<policy domain="path" rights="none" pattern="fd:*"/>
```

And this will also be included in ImageMagick's more secure policies by default.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xwc6-v6g8-pw2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25966
- https://github.com/ImageMagick/ImageMagick/commit/8d4c67a90ae458fb36393a05c0069e9123ac174c
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3

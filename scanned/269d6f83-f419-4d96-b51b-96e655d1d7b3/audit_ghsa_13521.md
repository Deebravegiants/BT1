# [H] Vulnerable version of libwebp and can be exploited with a malicious source image

## Summary
Severity: High
Advisory: GHSA-wqcr-xm43-hpqr
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-06
Source: https://github.com/advisories/GHSA-wqcr-xm43-hpqr
Type: github-advisory

## Affected
- NuGet: `ImageResizer.Plugins.FreeImage` — affected >=0

## Details
### Impact

This vulnerability affects deployments of FreeImage that involve decoding or processing malicious source .webp files. If you only process your own trusted files, this should not affect you, but **you should remove FreeImage from your project, as it is not maintained and presents a massive security risk**. 

If you are using FreeImage via  ImageResizer.Plugins.FreeImage, please utilize [Imageflow](https://github.com/imazen/imageflow) or [Imageflow.Server](https://github.com/imazen/imageflow-dotnet-server) instead, or upgrade to ImageResizer 5 and use ImageResizer.Plugins.Imageflow (enable Prereleases on NuGet to access). 

FreeImage relies on Google's [libwebp](https://github.com/webmproject/libwebp) library to decode .webp images, and is affected by the recent zero-day out-of-bounds write vulnerability [CVE-2023-4863](https://nvd.nist.gov/vuln/detail/CVE-2023-4863) and https://github.com/advisories/GHSA-j7hp-h8jx-5ppr. The libwebp vulnerability also affects Chrome, Android, macOS, and other consumers of the library).

libwebp patched [the vulnerability](https://github.com/webmproject/libwebp/commit/2af26267cdfcb63a88e5c74a85927a12d6ca1d76 ) and released [1.3.2](https://github.com/webmproject/libwebp/releases/tag/v1.3.2). FreeImage hasn't been updated since then and is presumed vulnerable. 

### Patches

None. FreeImage has not been updated in several years.

### Workarounds

 If you are using ImageResizer.Plugins.FreeImage, please utilize [Imageflow](https://github.com/imazen/imageflow) or [Imageflow.Server](https://github.com/imazen/imageflow-dotnet-server) instead, or upgrade to ImageResizer 5 and use ImageResizer.Plugins.Imageflow (enable Prereleases on NuGet to access). 

### References

https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
https://nvd.nist.gov/vuln/detail/CVE-2023-4863
https://github.com/webmproject/libwebp/commit/2af26267cdfcb63a88e5c74a85927a12d6ca1d76 
https://github.com/NoXF/libwebp-sys/commits/master

## References
- https://github.com/imazen/resizer/security/advisories/GHSA-wqcr-xm43-hpqr
- https://nvd.nist.gov/vuln/detail/CVE-2023-4863
- https://github.com/webmproject/libwebp/commit/2af26267cdfcb63a88e5c74a85927a12d6ca1d76
- https://github.com/NoXF/libwebp-sys/commits/master
- https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
- https://github.com/imazen/resizer

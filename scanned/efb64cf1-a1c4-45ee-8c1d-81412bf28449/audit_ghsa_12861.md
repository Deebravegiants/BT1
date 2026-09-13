# [M] Security bug in ConvertToSinglePlane when used with untrusted content from the DDS loader

## Summary
Severity: Medium
Advisory: GHSA-3w9w-9833-gcpv
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-3w9w-9833-gcpv
Type: github-advisory

## Affected
- NuGet: `directxtex_desktop_2019` — affected >=0 <2023.1.31.1
- NuGet: `directxtex_desktop_win10` — affected >=0 <2023.1.31.1
- NuGet: `directxtex_uwp` — affected >=0 <2023.1.31.1

## Details
### Impact
A memory overwrite bug was reported by a security researcher in the **ConvertToSinglePlane** method via the *texconv* command-line tool when given an invalid height for planar video textures such as NV12. This can be a potential security bug for any clients of the library who follow the same pattern.

This issue *does not* impact use of the DDS texture loader itself, only when combined with `ConvertToSinglePlane` for converting multi-planar video formats. All other functions in the library fail immediately if given images in planar formats.

### Patches
The fix to the specific area as well as general hardening can be found in [this PR](https://github.com/microsoft/DirectXTex/pull/307) and will be included in the This bug has been fixed in the January 31, 2023 or later release of DirectXTex.

### Workarounds
If your code makes use of **ConvertToSinglePlane**, you can validate that the width & height alignment requirements are met for the input image before calling the function.

## References
- https://github.com/microsoft/DirectXTex/security/advisories/GHSA-3w9w-9833-gcpv
- https://github.com/microsoft/DirectXTex/pull/307
- https://github.com/microsoft/DirectXTex

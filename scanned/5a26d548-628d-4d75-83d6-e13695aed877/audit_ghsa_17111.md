# [H] Use After Free in SixLabors.ImageSharp

## Summary
Severity: High
Advisory: GHSA-65x7-c272-7g7r
CVE: CVE-2024-27929
CWE: CWE-416
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-03-05
Source: https://github.com/advisories/GHSA-65x7-c272-7g7r
Type: github-advisory

## Affected
- NuGet: `SixLabors.ImageSharp` — affected >=3.0.0 <3.1.3
- NuGet: `SixLabors.ImageSharp` — affected >=0 <2.1.7

## Details
### Impact
A heap-use-after-free flaw was found in ImageSharp's InitializeImage() function of PngDecoderCore.cs file. This vulnerability is triggered when an attacker passes a specially crafted PNG image file to ImageSharp for conversion, potentially leading to information disclosure.

### Patches
The problem has been patched. All users are advised to upgrade to v3.1.3 or v2.1.7.

### Workarounds
None

### References
None

## References
- https://github.com/SixLabors/ImageSharp/security/advisories/GHSA-65x7-c272-7g7r
- https://nvd.nist.gov/vuln/detail/CVE-2024-27929
- https://github.com/SixLabors/ImageSharp/pull/2688
- https://github.com/SixLabors/ImageSharp

# [M] SixLabors.ImageSharp vulnerable to data leakage

## Summary
Severity: Medium
Advisory: GHSA-5x7m-6737-26cr
CVE: CVE-2024-32036
CWE: CWE-212, CWE-226
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-15
Source: https://github.com/advisories/GHSA-5x7m-6737-26cr
Type: github-advisory

## Affected
- NuGet: `SixLabors.ImageSharp` — affected >=0 <2.1.8
- NuGet: `SixLabors.ImageSharp` — affected >=3.0.0 <3.1.4

## Details
### Impact
A data leakage flaw was found in ImageSharp's JPEG and TGA decoders. This vulnerability is triggered when an attacker passes a specially crafted JPEG or TGA image file to a software using ImageSharp, potentially disclosing sensitive information from other parts of the software in the resulting image buffer.

### Patches
The problem has been patched. All users are advised to upgrade to v3.1.4 or v2.1.8.

### Workarounds
None

### References
None

## References
- https://github.com/SixLabors/ImageSharp/security/advisories/GHSA-5x7m-6737-26cr
- https://nvd.nist.gov/vuln/detail/CVE-2024-32036
- https://github.com/SixLabors/ImageSharp/commit/8f0b4d3e680e78d479a88e7b1472bccd8f096d68
- https://github.com/SixLabors/ImageSharp/commit/da5f09a42513489fe359578d81cec2f15ba588ba
- https://github.com/SixLabors/ImageSharp

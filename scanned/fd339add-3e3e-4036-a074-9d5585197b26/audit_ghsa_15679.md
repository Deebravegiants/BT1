# [M] SixLabors ImageSharp has Excessive Memory Allocation in Gif Decoder

## Summary
Severity: Medium
Advisory: GHSA-qxrv-gp6x-rc23
CVE: CVE-2024-41132
CWE: CWE-770, CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-07-22
Source: https://github.com/advisories/GHSA-qxrv-gp6x-rc23
Type: github-advisory

## Affected
- NuGet: `SixLabors.ImageSharp` — affected >=0 <2.1.9
- NuGet: `SixLabors.ImageSharp` — affected >=3.0.0 <3.1.5

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

A vulnerability discovered in the ImageSharp library, where the processing of specially crafted files can lead to excessive memory usage in the Gif decoder. The vulnerability is triggered when ImageSharp attempts to process image files that are designed to exploit this flaw.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

The problem has been patched. All users are advised to upgrade to v3.1.5 or v2.1.9.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Before calling `Image.Decode(Async)`, use `Image.Identify` to determine the image dimensions in order to enforce a limit.

### References
_Are there any links users can visit to find out more?_
- https://github.com/SixLabors/ImageSharp/pull/2759
- https://github.com/SixLabors/ImageSharp/pull/2764
- https://github.com/SixLabors/ImageSharp/pull/2770
- ImageSharp: [Security Considerations](https://docs.sixlabors.com/articles/imagesharp/security.html)
- ImageSharp.Web: [Securing Processing Commands](https://docs.sixlabors.com/articles/imagesharp.web/processingcommands.html#securing-processing-commands)

## References
- https://github.com/SixLabors/ImageSharp/security/advisories/GHSA-qxrv-gp6x-rc23
- https://nvd.nist.gov/vuln/detail/CVE-2024-41132
- https://github.com/SixLabors/ImageSharp/pull/2759
- https://github.com/SixLabors/ImageSharp/pull/2764
- https://github.com/SixLabors/ImageSharp/pull/2770
- https://github.com/SixLabors/ImageSharp/commit/59de13c8cc47f2b402e2c43aa7024511d029d515
- https://github.com/SixLabors/ImageSharp/commit/9816ca45016c5d3859986f3c600e8934bc450a56
- https://github.com/SixLabors/ImageSharp/commit/b496109051cc39feee1f6cde48fca6481de17f9a
- https://docs.sixlabors.com/articles/imagesharp.web/processingcommands.html#securing-processing-commands
- https://docs.sixlabors.com/articles/imagesharp/security.html
- https://github.com/SixLabors/ImageSharp

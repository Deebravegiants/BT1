# [M] SixLabors.ImageSharp vulnerable to Memory Allocation with Excessive Size Value

## Summary
Severity: Medium
Advisory: GHSA-g85r-6x2q-45w7
CVE: CVE-2024-32035
CWE: CWE-770, CWE-789
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-04-15
Source: https://github.com/advisories/GHSA-g85r-6x2q-45w7
Type: github-advisory

## Affected
- NuGet: `SixLabors.ImageSharp` — affected >=0 <2.1.8
- NuGet: `SixLabors.ImageSharp` — affected >=3.0.0 <3.1.4

## Details
### Impact

A vulnerability discovered in the ImageSharp library, where the processing of specially crafted files can lead to excessive memory usage in image decoders. The vulnerability is triggered when ImageSharp attempts to process image files that are designed to exploit this flaw. 

This flaw can be exploited to cause a denial of service (DoS) by depleting process memory, thereby affecting applications and services that rely on ImageSharp for image processing tasks. Users and administrators are advised to update to the latest version of ImageSharp that addresses this vulnerability to mitigate the risk of exploitation.

### Patches

The problem has been patched. All users are advised to upgrade to v3.1.4 or v2.1.8.

### Workarounds

Before calling `Image.Decode(Async)`, use `Image.Identify` to determine the image dimensions in order to enforce a limit.

### References

- ImageSharp: [Security Considerations](https://docs.sixlabors.com/articles/imagesharp/security.html)
- ImageSharp.Web: [Securing Processing Commands](https://docs.sixlabors.com/articles/imagesharp.web/processingcommands.html#securing-processing-commands)

## References
- https://github.com/SixLabors/ImageSharp/security/advisories/GHSA-g85r-6x2q-45w7
- https://nvd.nist.gov/vuln/detail/CVE-2024-32035
- https://github.com/SixLabors/ImageSharp/commit/b6b08ac3e7cea8da5ac1e90f7c0b67dd254535c3
- https://github.com/SixLabors/ImageSharp/commit/f21d64188e59ae9464ff462056a5e29d8e618b27
- https://docs.sixlabors.com/articles/imagesharp.web/processingcommands.html#securing-processing-commands
- https://docs.sixlabors.com/articles/imagesharp/security.html
- https://github.com/SixLabors/ImageSharp

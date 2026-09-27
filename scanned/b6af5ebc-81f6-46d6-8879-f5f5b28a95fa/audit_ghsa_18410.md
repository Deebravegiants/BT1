# [M] SixLabors ImageSharp Has Infinite Loop in GIF Decoder When Skipping Malformed Comment Extension Blocks

## Summary
Severity: Medium
Advisory: GHSA-rxmq-m78w-7wmc
CVE: CVE-2025-54575
CWE: CWE-400, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-rxmq-m78w-7wmc
Type: github-advisory

## Affected
- NuGet: `SixLabors.ImageSharp` — affected >=0 <2.1.11
- NuGet: `SixLabors.ImageSharp` — affected >=3.0.0 <3.1.11

## Details
### Impact
A specially crafted GIF file containing a malformed comment extension block (with a missing block terminator) can cause the ImageSharp GIF decoder to enter an infinite loop while attempting to skip the block. This leads to a denial of service. Applications processing untrusted GIF input should upgrade to a patched version.

### Patches
The problem has been patched. All users are advised to upgrade to v3.1.11 or v2.1.11.

### Workarounds
None.

## References
- https://github.com/SixLabors/ImageSharp/security/advisories/GHSA-rxmq-m78w-7wmc
- https://nvd.nist.gov/vuln/detail/CVE-2025-54575
- https://github.com/SixLabors/ImageSharp/issues/2953
- https://github.com/SixLabors/ImageSharp/commit/55e49262df9a057dff9b7807ed1b7bdb49187c3f
- https://github.com/SixLabors/ImageSharp/commit/833f3ceec35af6b775950e06f03b934546cefbf6
- https://github.com/SixLabors/ImageSharp

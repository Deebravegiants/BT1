# [H] DotNetZip Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-xhg6-9j5j-w4vf
CVE: CVE-2024-48510
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-xhg6-9j5j-w4vf
Type: github-advisory

## Affected
- NuGet: `DotNetZip` — affected >=1.10.1
- NuGet: `ProDotNetZip` — affected >=0 <1.19.0

## Details
Directory Traversal vulnerability in DotNetZip v.1.16.0 and before allows a remote attacker to execute arbitrary code via the src/Zip.Shared/ZipEntry.Extract.cs component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48510
- https://github.com/mihula/ProDotNetZip/pull/21
- https://github.com/mihula/ProDotNetZip/commit/18486ad6d13742a07a6755ef6edf60d7458f1854
- https://gist.github.com/thomas-chauchefoin-bentley-systems/855218959116f870f08857cce2aec731
- https://github.com/haf/DotNetZip.Semverd
- https://github.com/haf/DotNetZip.Semverd/blob/e487179b33a9a0f2631eed5fb04d2c952ea5377a/src/Zip.Shared/ZipEntry.Extract.cs#L1365-L1410
- https://www.nuget.org/packages/DotNetZip

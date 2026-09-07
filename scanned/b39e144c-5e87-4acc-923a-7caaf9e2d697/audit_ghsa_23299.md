# [M] Improper Limitation of a Pathname to a Restricted Directory in SharpZipLib

## Summary
Severity: Medium
Advisory: GHSA-cqj4-m2pc-v9m5
CVE: CVE-2018-1002208
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cqj4-m2pc-v9m5
Type: github-advisory

## Affected
- NuGet: `SharpZipLib` — affected >=0 <1.0.0-rc1

## Details
SharpZipLib before 1.0 RC1 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002208
- https://github.com/icsharpcode/SharpZipLib/issues/232
- https://github.com/icsharpcode/SharpZipLib/wiki/Release-1.0
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-DOTNET-SHARPZIPLIB-60247

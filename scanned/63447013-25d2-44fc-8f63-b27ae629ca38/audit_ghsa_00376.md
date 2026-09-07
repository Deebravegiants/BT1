# [M] DotNetZip Zip-Slip Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7378-6268-4278
CVE: CVE-2018-1002205
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-7378-6268-4278
Type: github-advisory

## Affected
- NuGet: `DotNetZip` — affected >=0 <1.11.0

## Details
DotNetZip.Semvered before 1.11.0 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002205
- https://github.com/haf/DotNetZip.Semverd/pull/121
- https://github.com/haf/DotNetZip.Semverd/commit/55d2c13c0cc64654e18fcdd0038fdb3d7458e366
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-DOTNET-DOTNETZIP-60245

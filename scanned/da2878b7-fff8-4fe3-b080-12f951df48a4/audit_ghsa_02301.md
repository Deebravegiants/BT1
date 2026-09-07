# [H] Path Traversal in elFinder.Net.Core

## Summary
Severity: High
Advisory: GHSA-mvvp-gwgc-5hrp
CVE: CVE-2021-23407
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-mvvp-gwgc-5hrp
Type: github-advisory

## Affected
- NuGet: `elFinder.Net.Core` — affected >=0 <1.2.4

## Details
This affects the package elFinder.Net.Core from 0 and before 1.2.4. The user-controlled file name is not properly sanitized before it is used to create a file system path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23407
- https://github.com/trannamtrung1st/elFinder.Net.Core/commit/5498c8a86b76ef089cfbd7ef8be014b61fa11c73
- https://github.com/trannamtrung1st/elFinder.Net.Core
- https://github.com/trannamtrung1st/elFinder.Net.Core/releases/tag/all-1.2.4
- https://snyk.io/vuln/SNYK-DOTNET-ELFINDERNETCORE-1315152

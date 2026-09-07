# [H] Directory Traversal in elFinder.AspNet

## Summary
Severity: High
Advisory: GHSA-pjxv-w3qj-j8m3
CVE: CVE-2021-23415
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-pjxv-w3qj-j8m3
Type: github-advisory

## Affected
- NuGet: `elFinder.AspNet` — affected >=0 <1.1.1

## Details
This affects the package elFinder.AspNet before 1.1.1.
 The user-controlled file name is not properly sanitized before it is used to create a file system path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23415
- https://github.com/mguinness/elFinder.AspNet/commit/675049b39284a9e84f0915c71d688da8ebc7d720
- https://github.com/mguinness/elFinder.AspNet
- https://snyk.io/vuln/SNYK-DOTNET-ELFINDERASPNET-1315153

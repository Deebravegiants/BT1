# [H] Umbraco CMS Authenticated File Upload

## Summary
Severity: High
Advisory: GHSA-h68c-4jh3-cp9j
CVE: CVE-2020-9471
CWE: CWE-434
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h68c-4jh3-cp9j
Type: github-advisory

## Affected
- NuGet: `UmbracoCMS.Core` — affected >=0

## Details
Umbraco Cloud 8.5.3 allows an authenticated file upload (and consequently Remote Code Execution) via the Install Packages functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9471
- https://github.com/umbraco/Umbraco-CMS
- https://gitlab.com/eLeN3Re/cve-2020-9471
- https://gitlab.com/eLeN3Re/cve-2020-9472/-/blob/master/CVE-2020-9472.pdf

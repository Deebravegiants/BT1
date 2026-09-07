# [M] Umbraco CMS has an arbitrary file upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-54mj-vcvj-q3v5
CVE: CVE-2025-67288
CWE: CWE-434, CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-22
Source: https://github.com/advisories/GHSA-54mj-vcvj-q3v5
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=0

## Details
An arbitrary file upload vulnerability in Umbraco CMS v16.3.3 allows attackers to execute arbitrary code via uploading a crafted PDF file. While Umbraco provides [hooks to perform file validation](https://docs.umbraco.com/umbraco-cms/reference/security/serverside-file-validation), it does not do implement filtering by default. Users are expected to implement their own validation.

Note: This vulnerability is [disputed by Ubraco](https://github.com/github/advisory-database/pull/6633).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67288
- https://github.com/github/advisory-database/pull/6633
- https://docs.umbraco.com/umbraco-cms/reference/security/serverside-file-validation
- https://github.com/umbraco/Umbraco-CMS
- https://github.com/vuquyen03/CVE/tree/main/CVE-2025-67288
- http://umbraco.com

# [M] Unrestricted Upload of File with Dangerous Type in Umbraco CMS

## Summary
Severity: Medium
Advisory: GHSA-j66f-h9hm-975m
CVE: CVE-2020-9472
CWE: CWE-434
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-j66f-h9hm-975m
Type: github-advisory

## Affected
- NuGet: `UmbracoCms` — affected >=0 <8.5.4

## Details
Umbraco CMS 8.5.3 allows an authenticated file upload (and consequently Remote Code Execution) via the Install Package functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9472
- https://gitlab.com/eLeN3Re/cve-2020-9472

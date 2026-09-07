# [M] Incorrect permission enforcement in UmbracoCms

## Summary
Severity: Medium
Advisory: GHSA-4vp3-vfww-8648
CVE: CVE-2020-29454
CWE: CWE-732
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-4vp3-vfww-8648
Type: github-advisory

## Affected
- NuGet: `UmbracoCms` — affected >=0 <8.10.0

## Details
Editors/LogViewerController.cs in Umbraco through 8.9.1 allows a user to visit a logviewer endpoint even if they lack Applications.Settings access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29454
- https://github.com/umbraco/Umbraco-CMS/pull/9361

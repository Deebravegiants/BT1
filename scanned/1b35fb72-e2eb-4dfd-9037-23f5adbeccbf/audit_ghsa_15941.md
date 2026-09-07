# [M] Umbraco has a Potential Code Execution Risk When Viewing SVG Files in Full Screen in Backoffice

## Summary
Severity: Medium
Advisory: GHSA-5955-cwv4-h7qh
CVE: CVE-2024-48927
CWE: CWE-74
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-5955-cwv4-h7qh
Type: github-advisory

## Affected
- NuGet: `UmbracoCms` — affected >=8.0.0 <8.18.15
- NuGet: `Umbraco.Cms` — affected >=10.0.0 <10.8.7
- NuGet: `Umbraco.Cms` — affected >=13.0.0 <13.5.2

## Details
### Impact
There is a potential risk of code execution for Backoffice users when they “preview” SVG files in full screen mode.

### Workarounds
Server-side file validation is available to strip script tags from file's content during the file upload process.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-5955-cwv4-h7qh
- https://nvd.nist.gov/vuln/detail/CVE-2024-48927
- https://github.com/umbraco/Umbraco-CMS

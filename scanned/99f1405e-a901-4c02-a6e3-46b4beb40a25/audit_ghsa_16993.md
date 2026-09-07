# [M] Blind SSRF Leads to Port Scan by using Webhooks

## Summary
Severity: Medium
Advisory: GHSA-74p6-39f2-23v3
CVE: CVE-2024-29035
CWE: CWE-918
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-74p6-39f2-23v3
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Core` — affected >=13.0.0 <13.1.1
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=13.0.0 <13.1.1

## Details
### Impact
Failing webhooks logs are available when solution is not in debug mode. Those logs can contain information that is critical.
 
### Affected Versions
Umbraco versions 13.0.0 - 13.1.1

### Patches
13.1.1

### Workarounds
Disabling webhooks functionality.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-74p6-39f2-23v3
- https://nvd.nist.gov/vuln/detail/CVE-2024-29035
- https://github.com/umbraco/Umbraco-CMS/commit/6b8067815c02ae43161966a8075a3585e1bc4de0
- https://github.com/umbraco/Umbraco-CMS

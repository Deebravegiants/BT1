# [M] XSS/HTML Injection Vulnerability in Umbraco Backoffice Components

## Summary
Severity: Medium
Advisory: GHSA-wv8v-rmw2-25wc
CVE: CVE-2025-24012
CWE: CWE-79
Ecosystem: NuGet, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-wv8v-rmw2-25wc
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.StaticAssets` — affected >=14.0.0 <14.3.2
- NuGet: `Umbraco.Cms.StaticAssets` — affected >=15.0.0 <15.1.2
- npm: `@umbraco-cms/backoffice` — affected >=14.0.0 <14.3.2
- npm: `@umbraco-cms/backoffice` — affected >=15.0.0 <15.1.2

## Details
### Impact
Authenticated users are able to exploit an XSS vulnerability when viewing certain localized backoffice components.

### Patches
Will be patched in 14.3.2 and 15.1.2.

Note:
This issue was reported by Pratik Patil from NetSPI @Nexusss-ppatil

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-wv8v-rmw2-25wc
- https://nvd.nist.gov/vuln/detail/CVE-2025-24012
- https://github.com/umbraco/Umbraco-CMS/commit/d4f8754f933895b3a329296e25ddea6f84a0aea2
- https://github.com/umbraco/Umbraco-CMS

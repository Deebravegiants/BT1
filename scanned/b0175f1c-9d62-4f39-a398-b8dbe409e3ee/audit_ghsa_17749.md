# [M] XSS/HTML Injection Vulnerability in Umbraco Preview Badge

## Summary
Severity: Medium
Advisory: GHSA-69cg-w8vm-h229
CVE: CVE-2024-10761
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-69cg-w8vm-h229
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=11.0.0 <13.5.3
- NuGet: `Umbraco.Cms` — affected >=14.0.0 <14.3.2
- NuGet: `Umbraco.Cms` — affected >=15.0.0 <15.1.2
- NuGet: `Umbraco.Cms` — affected >=10.8.7 <10.8.8
- NuGet: `Umbraco.Cms.Web.Common` — affected >=11.0.0 <13.5.3
- NuGet: `Umbraco.Cms.Web.Common` — affected >=14.0.0 <14.3.2
- NuGet: `Umbraco.Cms.Web.Common` — affected >=15.0.0 <15.1.2
- NuGet: `Umbraco.Cms.Web.Common` — affected >=10.8.7 <10.8.8

## Details
### Impact

Authenticated users are able to exploit an XSS vulnerability when viewing previewed content.

### Patches

Will be patched in 10.8.8, 13.5.3, 14.3.2 and 15.1.2.

### Workarounds

None available.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-69cg-w8vm-h229
- https://nvd.nist.gov/vuln/detail/CVE-2024-10761
- https://drive.google.com/file/d/1YoZgdlS3QT7Xu005j9RO-FFUT8RbB0Da/view?usp=sharing
- https://github.com/umbraco/Umbraco-CMS
- https://vuldb.com/?ctiid.282930
- https://vuldb.com/?id.282930
- https://vuldb.com/?submit.427091

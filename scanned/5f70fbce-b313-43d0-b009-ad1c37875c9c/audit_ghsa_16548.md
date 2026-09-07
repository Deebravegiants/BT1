# [M] Umbraco CMS Open Redirect Bypass Protection  

## Summary
Severity: Medium
Advisory: GHSA-j74q-mv2c-rxmp
CVE: CVE-2024-34071
CWE: CWE-601
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-j74q-mv2c-rxmp
Type: github-advisory

## Affected
- NuGet: `UmbracoCms.Core` — affected >=8.18.5 <8.18.14
- NuGet: `UmbracoCms.Core` — affected >=10.5.0 <10.8.6
- NuGet: `UmbracoCms.Core` — affected >=12.0.0 <12.3.10
- NuGet: `UmbracoCms.Core` — affected >=13.0.0 <13.3.1
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=8.18.5 <8.18.14
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=10.5.0 <10.8.6
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=12.0.0 <12.3.10
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=13.0.0 <13.3.1

## Details
### Impact
Umbraco have an endpoint that is vulnerable to open redirects. The endpoint is protected so it requires the user to be signed into backoffice, before the vulnerability is exposed.

### Affected Version

\>= 8.18.5, >= 10.5.0, >= 12.0.0, >= 13.0.0

### Patches
8.18.14, 10.8.6, 12.3.10, 13.3.1

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-j74q-mv2c-rxmp
- https://nvd.nist.gov/vuln/detail/CVE-2024-34071
- https://github.com/umbraco/Umbraco-CMS/commit/5f24de308584b9771240a6db1a34630a5114c450
- https://github.com/umbraco/Umbraco-CMS/commit/c17d4e1a600098ec524e4126f4395255476bc33f
- https://github.com/umbraco/Umbraco-CMS/commit/c8f71af646171074c13e5c34f74312def4512031
- https://github.com/umbraco/Umbraco-CMS/commit/d8df405db4ea884bb4b96f088d10d9a2070cf024
- https://github.com/umbraco/Umbraco-CMS

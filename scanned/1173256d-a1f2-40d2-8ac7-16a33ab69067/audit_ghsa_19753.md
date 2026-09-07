# [M] Umbraco Allows Improper API Access Control to Low-Privilege Users to Data Type Functionality

## Summary
Severity: Medium
Advisory: GHSA-6ffg-mjg7-585x
CVE: CVE-2025-27601
CWE: CWE-285, CWE-863
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-6ffg-mjg7-585x
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Api.Management` — affected >=15.0.0-rc1 <15.2.3
- NuGet: `Umbraco.Cms.Api.Management` — affected >=0 <14.3.3

## Details
### Impact
An improper API access control issue has been identified, allowing low-privilege, authenticated users to create and update data type information that should be restricted to users with access to the settings section.

### Patches
Will be patched in 14.3.3 and 15.2.3.

### Workarounds
None available.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-6ffg-mjg7-585x
- https://nvd.nist.gov/vuln/detail/CVE-2025-27601
- https://github.com/umbraco/Umbraco-CMS/commit/d9fb6df16e9adf8656181cac8497fc5ba23321cd
- https://github.com/umbraco/Umbraco-CMS/commit/ebb6a580dc1da2c772a99838dc7b4660bf77eb9c
- https://github.com/umbraco/Umbraco-CMS

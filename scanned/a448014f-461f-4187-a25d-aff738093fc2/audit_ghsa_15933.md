# [M] Umbraco CMS vulnerable to stored Cross-site Scripting in the "dictionary name" on Dictionary section

## Summary
Severity: Medium
Advisory: GHSA-c5g6-6xf7-qxp3
CVE: CVE-2024-47819
CWE: CWE-79, CWE-80
Ecosystem: NuGet, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-c5g6-6xf7-qxp3
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.StaticAssets` — affected >=14.0.0 <14.3.1
- npm: `@umbraco-cms/backoffice` — affected >=14.0.0 <14.3.1

## Details
### Impact
This can be leveraged to gain access to higher-privilege endpoints, e.g. if you get a user with admin privileges to run the code, you can potentially elevate all users and grant them admin privileges or access protected content.

### Patches
Will be patched in 14.3.1 and 15.0.0.

### Workarounds
Ensure that access to the Dictionary section is only granted to trusted users.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-c5g6-6xf7-qxp3
- https://nvd.nist.gov/vuln/detail/CVE-2024-47819
- https://github.com/umbraco/Umbraco-CMS

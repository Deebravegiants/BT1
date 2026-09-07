# [H] Umbraco allows possible Admin-level access to backoffice without Auth under rare conditions

## Summary
Severity: High
Advisory: GHSA-h8wc-r4jh-mg7m
CVE: CVE-2023-37267
CWE: CWE-284
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-13
Source: https://github.com/advisories/GHSA-h8wc-r4jh-mg7m
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Infrastructure` — affected >=9.0.0 <10.6.1
- NuGet: `Umbraco.Cms.Infrastructure` — affected >=11.0.0 <11.4.2
- NuGet: `Umbraco.Cms.Infrastructure` — affected >=12.0.0 <12.0.1
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=9.0.0 <10.6.1
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=11.0.0 <11.4.2
- NuGet: `Umbraco.Cms.Web.BackOffice` — affected >=12.0.0 <12.0.1

## Details
Under rare conditions, a restart of Umbraco can allow unauthorized users to gain admin-level permissions.

### Impact
An unauthorized user gaining admin-level access and permissions to the backoffice.

### Patches
10.6.1, 11.4.2, 12.0.1

### Workarounds
* Enabling the [Unattended Install](https://docs.umbraco.com/umbraco-cms/reference/configuration/unattendedsettings) feature will mean the vulnerability is not exploitable.
* Enabling IP restrictions to `*/install/*` and `*/umbraco/*` will limit the exposure to allowed IP addresses.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-h8wc-r4jh-mg7m
- https://nvd.nist.gov/vuln/detail/CVE-2023-37267
- https://github.com/umbraco/Umbraco-CMS/commit/1f26f2c6f3428833892cde5c6d8441fb041e410e
- https://github.com/umbraco/Umbraco-CMS/commit/20a4e475c8d7b91d263e4e103ef19f3644e7b569
- https://github.com/umbraco/Umbraco-CMS/commit/82eae48d098b9deecbdf86cf288b2b18020e1fed
- https://github.com/umbraco/Umbraco-CMS

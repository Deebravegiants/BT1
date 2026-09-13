# [H] Winter CMS Modules allows a sandbox bypass in Twig templates leading to data modification and deletion

## Summary
Severity: High
Advisory: GHSA-xhw3-4j3m-hq53
CVE: CVE-2024-54149
CWE: CWE-184
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-xhw3-4j3m-hq53
Type: github-advisory

## Affected
- Packagist: `winter/wn-cms-module` — affected >=1.2.0 <1.2.7
- Packagist: `winter/wn-cms-module` — affected >=1.1.0 <1.1.11
- Packagist: `winter/wn-cms-module` — affected >=0 <1.0.476

## Details
### Impact

Affected versions of Winter CMS allow users with access to the CMS templates sections that modify Twig files to bypass the sandbox placed on Twig files and modify resources such as theme customisation values or modify, or remove, templates in the theme even if not provided direct access via the permissions.

As all objects passed through to Twig are references to the live objects, it is also possible to also manipulate model data if models are passed directly to Twig, including changing attributes or even removing records entirely. In most cases, this is unwanted behavior and potentially dangerous.

To actively exploit this security issue, an attacker would need access to the Backend with a user account with any of the following permissions:
- `cms.manage_layouts`
- `cms.manage_pages`
- `cms.manage_partials`

The Winter CMS maintainers strongly recommend that these permissions only be reserved to trusted administrators and developers in general.

### Patches

In order to mitigate this issue, we have significantly increased the scope of the sandbox, effectively making all models and datasources read-only in Twig.

This security issue has been fixed as of https://github.com/wintercms/winter/commit/fb88e6fabde3b3278ce1844e581c87dcf7daee22.

### Workarounds

If you cannot upgrade, you may apply commit https://github.com/wintercms/winter/commit/fb88e6fabde3b3278ce1844e581c87dcf7daee22 to your Winter CMS installation manually to resolve this issue.

In the rare event that you were relying on being able to write to models/datasources within your Twig templates, you should instead use or create components to make changes to your models.

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-xhw3-4j3m-hq53
- https://nvd.nist.gov/vuln/detail/CVE-2024-54149
- https://github.com/wintercms/winter/commit/fb88e6fabde3b3278ce1844e581c87dcf7daee22
- https://github.com/wintercms/winter

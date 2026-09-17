# [M] Craft CMS: Arbitrary file read via SplFileObject in non-sandboxed template contexts

## Summary
Severity: Medium
Advisory: GHSA-957r-qf9p-67xw
CVE: CVE-2026-72779
CWE: CWE-184
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-957r-qf9p-67xw
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.6
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.2

## Details
The `create()` Twig function (introduced in 5.9.0) allows instantiation of arbitrary PHP classes from template code, restricted only by a 5-entry blocklist. `SplFileObject` is not in the blocklist, enabling arbitrary file read, including `.env` (security key, DB credentials) and the passwd file from non-sandboxed Twig template contexts, such as entry type title formats and URI formats. 

The sandbox correctly blocks `create()` in system email templates, so this finding applies only to admin-configured, non-sandboxed contexts that require `allowAdminChanges=true`.

## Prerequisites

- Admin access to the Craft control panel
- `allowAdminChanges` must be `true` (default in dev/staging, recommended `false` in production)
- Admin must be able to edit entry type settings (title format, URI format)
- Any user who subsequently creates an entry in the affected section triggers the file read

## Limitations

- Requires admin-level access: not exploitable by low-privilege users
- `allowAdminChanges` must be `true`: production best practices recommend `false`, which prevents entry type configuration changes
- Per Craft’s own severity guidelines, findings requiring `allowAdminChanges=true` are rated low
- The `create()` function is blocked by the Twig sandbox, so this cannot be exploited via system email templates or any other sandboxed context

## Impact

An admin user (or an attacker who has compromised an admin account) can read arbitrary files from the server filesystem by setting a malicious entry type title format using `create('SplFileObject', ['/path/to/file'])`. In production environments, this exposes `.env` files containing the `CRAFT_SECURITY_KEY`, database credentials, API keys, and other secrets. The file contents are rendered as entry titles visible to any user with permission to view entries in the affected section.

The impact is limited by the requirement for admin access and `allowAdminChanges=true`.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-957r-qf9p-67xw
- https://nvd.nist.gov/vuln/detail/CVE-2026-72779
- https://github.com/craftcms/cms/commit/7c96fd73df936a10e8f85ae6ef61a9fc3f277c12
- https://github.com/craftcms/cms/commit/87978f11c8f986c40ef41b941d79547230c4d6d9
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.2
- https://github.com/craftcms/cms/releases/tag/5.10.6
- https://www.vulncheck.com/advisories/craft-cms-rc1-before-arbitrary-file-read-via-splfileobject

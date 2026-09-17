# [M] Formie: Missing authorization in administrative settings allows low-privileged CP users to modify plugin configuration

## Summary
Severity: Medium
Advisory: GHSA-cvpc-hccg-wmw4
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-cvpc-hccg-wmw4
Type: github-advisory

## Affected
- Packagist: `verbb/formie` — affected >=0 <3.1.28

## Details
Formie contains a missing authorization vulnerability in administrative settings routes. An authenticated, non-admin Craft CMS control panel user with limited Formie access could directly access Formie settings pages and modify global plugin configuration.

In affected versions, Formie settings-related control panel routes did not consistently enforce the required settings permission on the server side. A low-privileged Craft CMS control panel user with limited Formie access could access /admin/formie/settings, save changes to global plugin settings, and access /admin/formie/settings/import-export.

The issue has been fixed by enforcing the formie-accessSettings permission across Formie settings controllers and related settings actions.

### Impact
An authenticated low-privileged CP user may be able to:
- Access Formie administrative settings.
- Modify global Formie plugin configuration.
- Access Formie import/export settings functionality.

This may allow configuration tampering and disruption of form-related workflows. Exploitation requires an authenticated Craft CMS control panel account.

## References
- https://github.com/verbb/formie/security/advisories/GHSA-cvpc-hccg-wmw4
- https://github.com/verbb/formie
- https://github.com/verbb/formie/releases/tag/3.1.28

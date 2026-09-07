# [M] Craft CMS Vulnerable to Stored XSS in Number Prefix & Suffix Fields

## Summary
Severity: Medium
Advisory: GHSA-9f5h-mmq6-2x78
CVE: CVE-2026-25496
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-9f5h-mmq6-2x78
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.22
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.16.18

## Details
## Summary

A stored XSS vulnerability exists in the Number field type settings. The Prefix and Suffix fields are rendered using the `|md|raw` Twig filter without proper escaping, allowing script execution when the Number field is displayed on users' profiles.

## Proof of Concept

### Required Permissions

- Administrator access
- `allowAdminChanges` is enabled in production, which is against our [security recommendations](https://craftcms.com/knowledge-base/securing-craft).

### Steps to Reproduce
1. Log in with an admin account
2. Navigate to **Settings** → **Fields** → **New field**
3. Choose **Number** as the field type
4. Set the **Prefix/Suffix Text** field to: <img width="611" height="908" alt="image" src="https://github.com/user-attachments/assets/63766ca4-4fa9-490b-8bea-37364137527d" />
```html
<img src=x onerror="alert('Number Prefix/Suffix XSS')" hidden>
```
5. Save the field
6. Add this field to any element (e.g., User Profile fields via **Settings** → **Users** → **User Fields**)
7. Navigate to your account (`/admin/myaccount`) or any user profile (`/admin/users/{id}`)
8. XSS executes when viewing the form <img width="1246" height="677" alt="image-1" src="https://github.com/user-attachments/assets/dafeb2b7-905f-4a4b-b3d6-1c16a905498f" />

## Mitigation
Sanitize prefix/suffix before rendering or use `|e` filter instead of `|raw`.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-9f5h-mmq6-2x78
- https://nvd.nist.gov/vuln/detail/CVE-2026-25496
- https://github.com/craftcms/cms/commit/cb5fb0e979e72f315c9178fc031883d49527f513
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.16.18
- https://github.com/craftcms/cms/releases/tag/5.8.22

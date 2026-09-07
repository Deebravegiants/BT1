# [M] Craft Commerce has Stored XSS in Product Type Name

## Summary
Severity: Medium
Advisory: GHSA-2h2m-v2mg-656c
CVE: CVE-2026-25484
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-2h2m-v2mg-656c
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.5.2
- Packagist: `craftcms/commerce` — affected >=4.0.0-RC1 <4.10.1

## Details
## Summary

Stored XSS via Product Type names. The name is not sanitized when displayed in user permissions settings.

The vulnerable input (source) is in Commerce (Product Type settings), but the sink is in CMS user permissions settings. Reporting to Commerce GHSA since the input originates here.

Users are recommended to update to the patched 5.5.2 release to mitigate the issue.

---
## Proof of Concept

### Required Permissions (Attacker)

- Admin access (to edit Commerce settings)

### Steps to Reproduce

1. Log in as attacker with admin permissions.
2. Go to **Commerce** -> **Settings** -> **Product Types** (`/admin/commerce/settings/producttypes`).
3. Create a new Product Type.
4. Set **Name** to:
```html
<img src=x onerror="alert('XSS-ProductType')" hidden>
```
5. Save the Product Type.
6. Go to **Users** -> Edit any user -> Click on **Permissions** tab (`/admin/users/{UserID}/permissions`).
7. Alert fires instantly (when the Product Type checkbox renders).

## Resources

https://github.com/craftcms/commerce/commit/7e1dedf06038c8e70dce0187b7048d4ab8ffb75c

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-2h2m-v2mg-656c
- https://nvd.nist.gov/vuln/detail/CVE-2026-25484
- https://github.com/craftcms/commerce/commit/7e1dedf06038c8e70dce0187b7048d4ab8ffb75c
- https://github.com/craftcms/commerce
- https://github.com/craftcms/commerce/releases/tag/4.10.1
- https://github.com/craftcms/commerce/releases/tag/5.5.2

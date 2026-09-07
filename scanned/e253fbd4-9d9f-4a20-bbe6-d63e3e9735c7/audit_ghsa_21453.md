# [C] ibexa/admin-ui vulnerable to Cross-site Scripting in content type name/shortname

## Summary
Severity: Critical
Advisory: GHSA-7644-cxp8-h23r
Ecosystem: Packagist
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-7644-cxp8-h23r
Type: github-advisory

## Affected
- Packagist: `ibexa/admin-ui` — affected >=4.2.0 <4.2.3

## Details
Critical severity. It is possible to inject JavaScript XSS in the content type entries "name" and "short name". To exploit this, one must already have permission to edit content types, which limits it in many cases to people who are already administrators. However, please verify which users have this permission. The fix ensures any injections are escaped.

## References
- https://github.com/ibexa/admin-ui/security/advisories/GHSA-7644-cxp8-h23r
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-009-critical-vulnerabilities-in-graphql-role-assignment-ct-editing-and-drafts-tooltips
- https://github.com/ibexa/admin-ui

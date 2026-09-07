# [C] ezplatform-admin-ui vulnerable to Cross-Site Scripting (XSS) 

## Summary
Severity: Critical
Advisory: GHSA-58h5-h554-429q
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-58h5-h554-429q
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=2.3.0 <2.3.26

## Details
It is possible to inject JavaScript XSS in the content type entries "name" and "short name". To exploit this, one must already have permission to edit content types, which limits it in many cases to people who are already administrators. However, please verify which users have this permission. The fix ensures any injections are escaped.

## References
- https://github.com/ezsystems/ezplatform-admin-ui/security/advisories/GHSA-58h5-h554-429q
- https://github.com/ezsystems/ezplatform-admin-ui/commit/29e156a7bbecca5abd946c99546a261679587d29
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-009-critical-vulnerabilities-in-graphql-role-assignment-ct-editing-and-drafts-tooltips
- https://github.com/ezsystems/ezplatform-admin-ui

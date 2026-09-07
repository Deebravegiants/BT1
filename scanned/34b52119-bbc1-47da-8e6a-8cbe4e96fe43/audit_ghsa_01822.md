# [M] XSS in richtext custom tag attributes in ezsystems/ezplatform-richtext

## Summary
Severity: Medium
Advisory: GHSA-9jp8-cwwx-p64q
Ecosystem: Packagist
Published: 2021-12-01
Source: https://github.com/advisories/GHSA-9jp8-cwwx-p64q
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=1.5.0 <1.5.25.1

## Details
The rich text editor does not escape attribute data when previewing custom tags. This means XSS is possible if custom tags are used, for users who have access to editing rich text content. Frontend content view is not affected, but the vulnerability could be used by editors to attack other editors. The fix ensures custom tag attribute data is escaped in the editor.

## References
- https://github.com/ezsystems/ezplatform-admin-ui/security/advisories/GHSA-9jp8-cwwx-p64q
- https://developers.ibexa.co/security-advisories/ibexa-sa-2021-010-xss-in-richtext-custom-tag-attributes
- https://github.com/ezsystems/ezplatform-admin-ui

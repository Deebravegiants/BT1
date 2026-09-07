# [H] eZ Platform Admin UI Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-q73v-79x3-jv2w
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-q73v-79x3-jv2w
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=1.3.0 <1.3.5
- Packagist: `ezsystems/ezplatform-admin-ui` — affected >=1.4.0 <1.4.4

## Details
This security advisory fixes a severe vulnerability in the eZ Platform Admin UI, and we recommend that you install it as soon as possible. Parts of the Admin UI are vulnerable to XSS injection. All 2.x sites are at risk, and particularly those that allow user generated content. The update adds the necessary escaping of injected code. This resolves the issue both for code that has already been injected, and any future such code.

To install, use Composer to update "ezsystems/ezplatform-admin-ui" and "ezsystems/ezplatform-page-builder" to one of the "Resolving versions" mentioned above. (ezplatform-page-builder exists only in eZ Platform Enterprise Edition.)

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezplatform-admin-ui/CVE-2019-12139.yaml
- https://github.com/ezsystems/ezplatform-admin-ui
- https://share.ez.no/community-project/security-advisories/ezsa-2019-001-xss-in-admin-ui
- https://web.archive.org/web/20201207160038/https://share.ez.no/community-project/security-advisories/ezsa-2019-001-xss-in-admin-ui

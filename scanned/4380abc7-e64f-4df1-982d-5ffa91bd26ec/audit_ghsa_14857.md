# [C] willdurand/js-translation-bundle potential path traversal attack and remote code injection

## Summary
Severity: Critical
Advisory: GHSA-x86x-qhf8-f37w
CWE: CWE-22, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-x86x-qhf8-f37w
Type: github-advisory

## Affected
- Packagist: `willdurand/js-translation-bundle` — affected >=0 <2.1.1

## Details
A path traversal and a javascript code injection vulnerabilities were identified in willdurand/js-translation-bundle versions prior to 2.1.1.

## References
- https://github.com/willdurand/BazingaJsTranslationBundle/commit/7accee93569c3f3d2379f035a41ece66522801fc
- https://github.com/willdurand/BazingaJsTranslationBundle/commit/df6c0fd603c0192ebc5584991a52a1092c5f60bd
- https://github.com/FriendsOfPHP/security-advisories/blob/master/willdurand/js-translation-bundle/2014-07-29-1.yaml
- https://github.com/willdurand/BazingaJsTranslationBundle
- https://github.com/willdurand/BazingaJsTranslationBundle/releases/tag/v2.1.1

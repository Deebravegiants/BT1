# [H] XML External Entity (XXE) Processing in TYPO3 Core

## Summary
Severity: High
Advisory: GHSA-qffc-gwpp-m2xr
Ecosystem: Packagist
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-qffc-gwpp-m2xr
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.19
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.4

## Details
All XML processing within the TYPO3 CMS are vulnerable to XEE processing. This can lead to load internal and/or external (file) content within an XML structure. Furthermore it is possible to inject arbitrary files for an XML Denial of Service attack. For more information on that topic see https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-02-23-1.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-005

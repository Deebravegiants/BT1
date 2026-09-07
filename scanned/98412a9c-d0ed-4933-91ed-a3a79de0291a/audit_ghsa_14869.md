# [H] Insecure Deserialization in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-8h28-f46f-m87h
CWE: CWE-502
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-8h28-f46f-m87h
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.5.0 <8.7.17
- Packagist: `typo3/cms` — affected >=9.0.0 <9.3.2

## Details
It has been discovered that the Form Framework (system extension "form") is vulnerable to Insecure Deserialization when being used with the additional PHP PECL package “yaml”, which is capable of unserializing YAML contents to PHP objects. A valid backend user account as well as having PHP setting "yaml.decode_php" enabled is needed to exploit this vulnerability (which is the default value according to PHP documentation).

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-07-12-4.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-004

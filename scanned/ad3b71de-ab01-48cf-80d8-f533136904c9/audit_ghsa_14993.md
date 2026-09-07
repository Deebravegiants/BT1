# [M] Typo3 Arbitrary Code Execution and Cross-Site Scripting in Backend API

## Summary
Severity: Medium
Advisory: GHSA-hww5-6x85-mc24
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-hww5-6x85-mc24
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.27
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.8

## Details
Backend API configuration using Page TSconfig is vulnerable to arbitrary code execution and cross-site scripting. TSconfig fields of page properties in backend forms can be used to inject malicious sequences. Field tsconfig_includes is vulnerable to directory traversal leading to same scenarios as having direct access to TSconfig settings.

A valid backend user account having access to modify values for fields pages.TSconfig and pages.tsconfig_includes is needed in order to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-06-25-4.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2019-019
